from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SystemSetting, User
from app.deps import require_roles, ADMINS, log_action
from app.utils.security import decrypt_secret
from app.voip.voipms import ADAPTER as VOIPMS_ADAPTER

router = APIRouter(prefix="/api/voip", tags=["voip"])

SECRET_KEYS = {"voip_sip_password", "voip_api_password"}


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
    if provider != "voipms":
        return {"ok": False, "provider": provider or "", "message": "Select VoIP.ms as the VOIP provider before testing.", "data": {}}

    config = {
        "sip_username": _value(db, "voip_sip_username"),
        "api_username": _value(db, "voip_api_username"),
        "api_password": _value(db, "voip_api_password"),
        "server": _value(db, "voip_server"),
        "port": _value(db, "voip_port", "5060"),
    }
    result = VOIPMS_ADAPTER.test(config)
    log_action(db, current_user, "test_voip_provider", "voip", None, {"provider": provider, "ok": result.ok}, request)
    return {"ok": result.ok, "provider": result.provider, "message": result.message, "data": result.data}
