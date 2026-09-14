from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SystemSetting, User
from app.deps import require_roles, ADMINS, log_action
from app.utils.security import decrypt_secret
from app.voip.yeastar import ADAPTER as YEASTAR_ADAPTER

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
