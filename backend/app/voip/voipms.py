from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
import socket

from app.voip.base import VoIPProviderAdapter, VoIPAdapterResult


class VoIPmsAdapter(VoIPProviderAdapter):
    provider_key = "voipms"
    display_name = "VoIP.ms"
    API_URL = "https://voip.ms/api/v1/rest.php"

    def _api(self, username: str, password: str, method: str, **params: Any) -> Dict[str, Any]:
        query = {"api_username": username, "api_password": password, "method": method, "content_type": "json"}
        query.update({k: v for k, v in params.items() if v not in (None, "")})
        url = self.API_URL + "?" + urlencode(query)
        req = Request(url, headers={"User-Agent": "LeadCRM-VOIP-Lab/2.8.2"})
        try:
            with urlopen(req, timeout=15) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            return {"status": "error", "error": f"HTTP {exc.code}"}
        except URLError as exc:
            return {"status": "error", "error": f"Network error: {exc.reason}"}
        except TimeoutError:
            return {"status": "error", "error": "Provider API timeout"}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "error", "error": "Invalid JSON response from provider API"}

    def test(self, config: Dict[str, Any]) -> VoIPAdapterResult:
        api_username = (config.get("api_username") or "").strip()
        api_password = config.get("api_password") or ""
        sip_username = (config.get("sip_username") or "").strip()
        pop = (config.get("server") or "").strip()

        if not api_username or not api_password:
            return VoIPAdapterResult(False, self.provider_key, "VoIP.ms API credentials are not configured.", {})
        if not sip_username:
            return VoIPAdapterResult(False, self.provider_key, "VoIP.ms SIP username is not configured.", {})
        if not pop:
            return VoIPAdapterResult(False, self.provider_key, "VoIP.ms POP/SIP server is not configured.", {})

        try:
            socket.getaddrinfo(pop, int(config.get("port") or 5060), type=socket.SOCK_DGRAM)
            dns_ok = True
        except (OSError, ValueError):
            dns_ok = False

        registration = self._api(
            api_username,
            api_password,
            "getRegistrationStatus",
            account=sip_username,
        )
        if registration.get("status") != "success":
            return VoIPAdapterResult(
                False,
                self.provider_key,
                "VoIP.ms API authentication/request failed.",
                {"dns_ok": dns_ok, "api": registration},
            )

        registered = str(registration.get("registered", "")).lower() in {"yes", "true", "1"}
        return VoIPAdapterResult(
            True,
            self.provider_key,
            "VoIP.ms API connection succeeded.",
            {
                "dns_ok": dns_ok,
                "sip_account": sip_username,
                "pop_server": pop,
                "registered": registered,
                "registration": registration,
            },
        )


ADAPTER = VoIPmsAdapter()
