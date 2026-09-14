from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SystemSetting, User, VoIPExtensionMapping
from app.deps import require_roles, ADMINS, log_action
from app.utils.security import decrypt_secret
from app.voip.yeastar import ADAPTER as YEASTAR_ADAPTER
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/voip", tags=["voip"])


def _value(db: Session, key: str, default: str = "") -> str:
    row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not row or not row.value:
        return default
    if row.is_secret:
        return decrypt_secret(row.value) or ""
    return row.value


@router.post("/test")
def test_voip(request: Request, current_user: User = Depends(require_roles(*ADMINS)), db: Session = Depends(get_db)):
    provider = _value(db, "voip_provider").strip().lower()
    if provider != "yeastar_s_series":
        return {"ok": False, "provider": provider or "", "message": "Select Yeastar S-Series as the VOIP provider before testing.", "data": {}}

    config = {
        "server": _value(db, "voip_server"),
        "api_username": _value(db, "voip_api_username"),
        "api_password": _value(db, "voip_api_password"),
        "api_protocol": _value(db, "voip_api_protocol", "https"),
        "api_port": _value(db, "voip_api_port", "8088"),
        "api_version": _value(db, "voip_api_version", "2.0.0"),
        "event_port": _value(db, "voip_event_port", "0"),
        "verify_tls": _value(db, "voip_tls_verify", "false"),
    }
    result = YEASTAR_ADAPTER.test(config)
    log_action(db, current_user, "test_voip_provider", "voip", None, {"provider": provider, "ok": result.ok}, request)
    return {"ok": result.ok, "provider": result.provider, "message": result.message, "data": result.data}


class ExtensionMappingIn(BaseModel):
    user_id: int
    extension_number: str
    is_active: bool = True


def _yeastar_config(db: Session) -> dict:
    return {
        "server": _value(db, "voip_server"),
        "api_username": _value(db, "voip_api_username"),
        "api_password": _value(db, "voip_api_password"),
        "api_protocol": _value(db, "voip_api_protocol", "https"),
        "api_port": _value(db, "voip_api_port", "8088"),
        "api_version": _value(db, "voip_api_version", "2.0.0"),
        "event_port": _value(db, "voip_event_port", "0"),
        "verify_tls": _value(db, "voip_tls_verify", "false"),
    }


@router.get("/extensions")
def list_yeastar_extensions(request: Request, current_user: User = Depends(require_roles(*ADMINS)), db: Session = Depends(get_db)):
    provider = _value(db, "voip_provider").strip().lower()
    if provider != "yeastar_s_series":
        return {"ok": False, "provider": provider, "message": "Select Yeastar S-Series as the VOIP provider first.", "extensions": [], "mappings": []}
    result = YEASTAR_ADAPTER.query_extensions(_yeastar_config(db))
    mappings = db.query(VoIPExtensionMapping).filter(VoIPExtensionMapping.provider == provider, VoIPExtensionMapping.is_active.is_(True)).all()
    mapping_rows = [{"id": m.id, "user_id": m.user_id, "extension_number": m.extension_number, "is_active": m.is_active, "user_name": m.user.full_name if m.user else ""} for m in mappings]
    log_action(db, current_user, "query_voip_extensions", "voip", None, {"provider": provider, "ok": result.ok}, request)
    return {"ok": result.ok, "provider": result.provider, "message": result.message, "extensions": result.data.get("extensions", []), "mappings": mapping_rows}


@router.put("/extensions/mapping")
def save_yeastar_extension_mapping(payload: ExtensionMappingIn, request: Request, current_user: User = Depends(require_roles(*ADMINS)), db: Session = Depends(get_db)):
    provider = _value(db, "voip_provider").strip().lower()
    if provider != "yeastar_s_series":
        raise HTTPException(400, "Select Yeastar S-Series as the VOIP provider first.")
    extension_number = str(payload.extension_number).strip()
    if not extension_number or len(extension_number) > 20:
        raise HTTPException(400, "Invalid extension number.")
    if not extension_number.isdigit():
        raise HTTPException(400, "Extension number must contain digits only.")
    user = db.query(User).filter(User.id == payload.user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(404, "Active CRM user not found.")
    existing_ext = db.query(VoIPExtensionMapping).filter(
        VoIPExtensionMapping.provider == provider,
        VoIPExtensionMapping.extension_number == extension_number,
        VoIPExtensionMapping.user_id != payload.user_id,
        VoIPExtensionMapping.is_active.is_(True),
    ).first()
    if existing_ext:
        raise HTTPException(409, f"Extension {extension_number} is already mapped to another CRM user.")
    row = db.query(VoIPExtensionMapping).filter(
        VoIPExtensionMapping.provider == provider, VoIPExtensionMapping.user_id == payload.user_id
    ).first()
    if row:
        row.extension_number = extension_number
        row.is_active = payload.is_active
    else:
        row = VoIPExtensionMapping(provider=provider, user_id=payload.user_id, extension_number=extension_number, is_active=payload.is_active)
        db.add(row)
    db.commit()
    db.refresh(row)
    log_action(db, current_user, "map_voip_extension", "voip_extension_mapping", row.id, {"provider": provider, "user_id": user.id, "extension_number": extension_number}, request)
    return {"id": row.id, "user_id": row.user_id, "extension_number": row.extension_number, "is_active": row.is_active, "user_name": user.full_name}


@router.delete("/extensions/mapping/{mapping_id}")
def delete_yeastar_extension_mapping(mapping_id: int, request: Request, current_user: User = Depends(require_roles(*ADMINS)), db: Session = Depends(get_db)):
    row = db.query(VoIPExtensionMapping).filter(VoIPExtensionMapping.id == mapping_id, VoIPExtensionMapping.provider == "yeastar_s_series").first()
    if not row:
        raise HTTPException(404, "Extension mapping not found.")
    details = {"provider": row.provider, "user_id": row.user_id, "extension_number": row.extension_number}
    db.delete(row)
    db.commit()
    log_action(db, current_user, "unmap_voip_extension", "voip_extension_mapping", mapping_id, details, request)
    return {"ok": True}
