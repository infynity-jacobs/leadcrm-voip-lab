# v2.8.0 — VOIP Lab (Provider-Neutral Foundation)

- Separate test build for VOIP work; does not modify the production v2.7.x application.
- Added Settings → VOIP configuration section.
- Added provider-neutral system type choices: Generic SIP/WebRTC, Asterisk/FreePBX, SIP Trunk/VOIP Provider, PBX API/WebSocket, Other.
- No Yeastar adapter or vendor-specific implementation is included.
- Configuration-only foundation: no calls are placed or received in this build.
- Reserved architecture for per-user extensions, encrypted SIP credentials, browser WebRTC/SIP, call events and Call Log integration in later phases.
- Test installation uses isolated `/opt/leadcrm-voip-lab` paths and `leadcrm_voip_lab` database.
- No database migration required.
