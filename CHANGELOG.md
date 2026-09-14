# Changelog

## v2.8.5 - Yeastar API test hardening

- Matches the verified S50 API 2.0 HTTPS login request.
- Adds robust TLS/network/timeout/connection-reset handling instead of generic HTTP 500 errors.
- Maps Yeastar error 20003 to a clear invalid-credentials message.
- Tests `deviceinfo/query` after login and performs best-effort API logout.
- Never returns API tokens or secrets to the browser.
- Settings test now saves current form values before running, preventing stale protocol/credential tests.


## v2.8.5 - Yeastar adapter diagnostics fix
- Hardened Yeastar HTTPS/network exception handling so protocol, TLS, timeout and connection failures return useful test results instead of HTTP 500.
- Login request matches the verified S-Series API 2.0 flow: JSON POST, lowercase MD5 API password, API version and event port.
- Yeastar error 20003 is reported as an API credential rejection with a clear instruction to re-enter the saved CRM API password.
- Added HTTP status/error type diagnostics without exposing API passwords, hashes or tokens.
- Added deviceinfo query after login and best-effort logout after the connection test.
- Kept HTTPS 8088 with TLS verification disabled as the lab default.

## v2.8.3 - Yeastar S-Series adapter lab
- Removed the VoIP.ms adapter and VoIP.ms-specific settings/UI.
- Added Yeastar S-Series API adapter.
- Added Yeastar API 2.0 login with MD5 password hashing.
- Added PBX information query after successful login.
- Added encrypted Yeastar API password setting.
- Added configurable Yeastar API protocol, port, version, event port and TLS verification.
- Added admin-only "Test Yeastar Connection" action.
- Kept the lab isolated from the production Lead CRM.
- Browser calling, extension provisioning and call-log integration remain out of scope for this release.

## v2.8.2 - VoIP.ms adapter lab
- Superseded by v2.8.3 Yeastar adapter lab for the current VOIP test direction.

## v2.8.5
- Yeastar S-Series HTTPS adapter now pins its PBX connection to TLS 1.2.
- This avoids TLS 1.3 handshake failures with older S-Series embedded web servers while leaving system-wide OpenSSL settings unchanged.
- Preserves certificate verification toggle and improved network/API diagnostics from v2.8.4.

## v2.9.0 - Yeastar Extension Integration Lab

- Added Yeastar S-Series extension discovery using API 2.0 `extension/query` with `number=all`.
- Sanitized PBX extension responses so registration passwords and other sensitive extension fields are never returned to the CRM UI.
- Added persistent CRM-user to Yeastar-extension mappings.
- Added Settings → VOIP extension discovery, status display, mapping, unmapping, and refresh controls.
- Added migration `0006_voip_extension_mappings.sql`.
- Kept call control, browser WebRTC/SIP, and PBX configuration changes out of this milestone.
