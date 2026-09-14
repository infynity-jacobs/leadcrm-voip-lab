from typing import Any, Dict, Optional
from http.client import HTTPResponse
from urllib.error import HTTPError, URLError
import hashlib
import json
import socket
import ssl

from app.voip.base import VoIPProviderAdapter, VoIPAdapterResult


class YeastarAdapter(VoIPProviderAdapter):
    provider_key = "yeastar_s_series"
    display_name = "Yeastar S-Series"

    ERROR_MESSAGES = {
        "20003": "Invalid API username or password. Re-enter the Yeastar API credentials, save them, and retry.",
    }

    def _ssl_context(self, verify: bool) -> ssl.SSLContext:
        # The Yeastar S-Series lab PBX accepts TLS 1.2 with
        # AES256-GCM-SHA384, but rejects the default OpenSSL 3 ClientHello.
        # Keep this compatibility setting scoped to the Yeastar adapter.
        if verify:
            context = ssl.create_default_context()
        else:
            context = ssl._create_unverified_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers("AES256-GCM-SHA384")
        return context

    def _request_json(self, url: str, payload: Optional[Dict[str, Any]], verify_tls: bool) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else b"{}"
        parsed_url = url.split("://", 1)
        if len(parsed_url) != 2:
            return {"status": "Failed", "error_type": "url", "error": "Invalid Yeastar API URL."}
        scheme, remainder = parsed_url
        authority, _, path = remainder.partition("/")
        host, sep, port_text = authority.rpartition(":")
        if not sep:
            host, port_text = authority, "443" if scheme.lower() == "https" else "80"
        try:
            port = int(port_text)
        except ValueError:
            return {"status": "Failed", "error_type": "url", "error": "Invalid Yeastar API port."}
        request_path = "/" + path
        if scheme.lower() not in {"http", "https"}:
            return {"status": "Failed", "error_type": "url", "error": "Unsupported Yeastar API protocol."}

        raw_sock = None
        sock = None
        try:
            raw_sock = socket.create_connection((host, port), timeout=10)
            if scheme.lower() == "https":
                # Deliberately omit server_hostname/SNI. This matches the
                # known-good Python TLS test against the older Yeastar Boa server.
                context = self._ssl_context(verify_tls)
                sock = context.wrap_socket(raw_sock, server_hostname=None)
            else:
                sock = raw_sock

            request = (
                f"POST {request_path} HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                "Content-Type: application/json; charset=utf-8\r\n"
                "Accept: application/json\r\n"
                "User-Agent: LeadCRM-VOIP-Lab/2.8.6\r\n"
                f"Content-Length: {len(data)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii") + data
            sock.sendall(request)
            response = HTTPResponse(sock)
            response.begin()
            raw = response.read().decode("utf-8", errors="replace")
            if response.status >= 400:
                try:
                    result = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    result = {}
                result.setdefault("status", "Failed")
                result.setdefault("error", f"Yeastar API returned HTTP {response.status}.")
                result["http_status"] = response.status
                return result
        except ssl.SSLError as exc:
            return {"status": "Failed", "error_type": "tls", "error": f"TLS error: {exc}"}
        except (socket.timeout, TimeoutError):
            return {"status": "Failed", "error_type": "timeout", "error": "Yeastar API connection timed out."}
        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError) as exc:
            return {"status": "Failed", "error_type": "connection", "error": f"PBX connection failed: {exc}"}
        except (URLError, OSError) as exc:
            reason = getattr(exc, "reason", exc)
            return {"status": "Failed", "error_type": "network", "error": f"Network/connection error: {reason}"}
        except Exception as exc:
            return {"status": "Failed", "error_type": "request", "error": f"Yeastar API request failed: {exc}"}
        finally:
            try:
                if sock is not None:
                    sock.close()
                elif raw_sock is not None:
                    raw_sock.close()
            except Exception:
                pass

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"status": "Failed", "error_type": "response", "error": "Yeastar PBX returned a non-JSON response."}

    def _failure_message(self, response: Dict[str, Any], prefix: str) -> str:
        errno = str(response.get("errno") or "").strip()
        if errno in self.ERROR_MESSAGES:
            return self.ERROR_MESSAGES[errno]
        if response.get("error"):
            return f"{prefix}: {response['error']}"
        if errno:
            return f"{prefix} (Yeastar error {errno})."
        return f"{prefix}."

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
            return VoIPAdapterResult(False, self.provider_key, "Yeastar API credentials are not configured. Save the API username and password first.", {})
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
        login_payload: Dict[str, Any] = {
            "username": api_user,
            "password": md5_password,
            "version": api_version,
            # Keep port="0" to match the known-good S50 API 2.0 login test.
            "port": event_port if event_port else "0",
        }

        login = self._request_json(f"{base}/login", login_payload, verify_tls)
        if str(login.get("status", "")).lower() != "success" or not login.get("token"):
            return VoIPAdapterResult(
                False,
                self.provider_key,
                self._failure_message(login, "Yeastar API login failed"),
                {
                    "dns_ok": dns_ok,
                    "api_protocol": api_protocol,
                    "api_port": api_port,
                    "api_version": api_version,
                    "yeastar_errno": login.get("errno"),
                    "error_type": login.get("error_type"),
                },
            )

        token = str(login["token"])
        try:
            device = self._request_json(f"{base}/deviceinfo/query?token={token}", None, verify_tls)
            if str(device.get("status", "")).lower() != "success":
                return VoIPAdapterResult(
                    False,
                    self.provider_key,
                    self._failure_message(device, "Yeastar API login succeeded, but PBX information query failed"),
                    {"dns_ok": dns_ok, "api_login": True, "device_query_ok": False},
                )

            info = device.get("deviceinfo") or device.get("device_info") or {}
            return VoIPAdapterResult(
                True,
                self.provider_key,
                "Yeastar API connection succeeded and PBX information was received.",
                {
                    "dns_ok": dns_ok,
                    "api_login": True,
                    "api_protocol": api_protocol,
                    "api_port": api_port,
                    "api_version": api_version,
                    "device_info": info,
                },
            )
        finally:
            # Best-effort logout. Never expose or log the token.
            try:
                self._request_json(f"{base}/logout?token={token}", None, verify_tls)
            except Exception:
                pass


ADAPTER = YeastarAdapter()
