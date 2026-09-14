from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import hashlib
import json
import socket
import ssl

from app.voip.base import VoIPProviderAdapter, VoIPAdapterResult


class YeastarAdapter(VoIPProviderAdapter):
    provider_key = "yeastar_s_series"
    display_name = "Yeastar S-Series"

    def _ssl_context(self, verify: bool) -> Optional[ssl.SSLContext]:
        if verify:
            return None
        return ssl._create_unverified_context()

    def _post_json(self, url: str, payload: Dict[str, Any], verify_tls: bool) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "LeadCRM-VOIP-Lab/2.8.3",
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=10, context=self._ssl_context(verify_tls)) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            return {"status": "Failed", "error": f"HTTP {exc.code}"}
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            return {"status": "Failed", "error": f"Network error: {reason}"}
        except TimeoutError:
            return {"status": "Failed", "error": "Yeastar API timeout"}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "Failed", "error": "Invalid JSON response from Yeastar PBX"}

    def _get_json(self, url: str, verify_tls: bool) -> Dict[str, Any]:
        req = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "LeadCRM-VOIP-Lab/2.8.3"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=10, context=self._ssl_context(verify_tls)) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            return {"status": "Failed", "error": f"HTTP {exc.code}"}
        except URLError as exc:
            reason = getattr(exc, "reason", exc)
            return {"status": "Failed", "error": f"Network error: {reason}"}
        except TimeoutError:
            return {"status": "Failed", "error": "Yeastar API timeout"}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "Failed", "error": "Invalid JSON response from Yeastar PBX"}

    def test(self, config: Dict[str, Any]) -> VoIPAdapterResult:
        host = (config.get("server") or "").strip()
        api_user = (config.get("api_username") or "").strip()
        api_password = config.get("api_password") or ""
        api_protocol = (config.get("api_protocol") or "https").strip().lower()
        api_port = str(config.get("api_port") or "8088").strip()
        api_version = (config.get("api_version") or "2.0.0").strip()
        event_port = str(config.get("event_port") or "0").strip()
        verify_tls = str(config.get("verify_tls") or "false").lower() in {"true", "1", "yes", "on"}

        if not host:
            return VoIPAdapterResult(False, self.provider_key, "Yeastar PBX host/IP is not configured.", {})
        if not api_user or not api_password:
            return VoIPAdapterResult(False, self.provider_key, "Yeastar API credentials are not configured.", {})
        if api_protocol not in {"http", "https"}:
            return VoIPAdapterResult(False, self.provider_key, "Yeastar API protocol must be HTTP or HTTPS.", {})
        try:
            port_num = int(api_port)
            if not (1 <= port_num <= 65535):
                raise ValueError
        except ValueError:
            return VoIPAdapterResult(False, self.provider_key, "Yeastar API port is invalid.", {})

        try:
            socket.getaddrinfo(host, port_num, type=socket.SOCK_STREAM)
            dns_ok = True
        except OSError:
            dns_ok = False

        base = f"{api_protocol}://{host}:{api_port}/api/v{api_version}"
        md5_password = hashlib.md5(api_password.encode("utf-8")).hexdigest()
        login_payload = {
            "username": api_user,
            "password": md5_password,
            "version": api_version,
            "port": event_port,
        }
        login = self._post_json(f"{base}/login", login_payload, verify_tls)
        if str(login.get("status", "")).lower() != "success" or not login.get("token"):
            errno = login.get("errno")
            detail = f" (error {errno})" if errno else ""
            return VoIPAdapterResult(
                False,
                self.provider_key,
                f"Yeastar API login failed{detail}.",
                {"dns_ok": dns_ok, "api_protocol": api_protocol, "api_port": api_port, "api_version": api_version},
            )

        token = str(login["token"])
        device = self._get_json(f"{base}/deviceinfo/query?token={token}", verify_tls)
        if str(device.get("status", "")).lower() != "success":
            return VoIPAdapterResult(
                False,
                self.provider_key,
                "Yeastar API login succeeded, but PBX information could not be queried.",
                {"dns_ok": dns_ok, "api_login": True, "device_query": device},
            )

        info = device.get("deviceinfo") or device.get("device_info") or {}
        # Do not return the API token to the browser.
        return VoIPAdapterResult(
            True,
            self.provider_key,
            "Yeastar API connection succeeded.",
            {
                "dns_ok": dns_ok,
                "api_login": True,
                "api_protocol": api_protocol,
                "api_port": api_port,
                "api_version": api_version,
                "device_info": info,
            },
        )


ADAPTER = YeastarAdapter()
