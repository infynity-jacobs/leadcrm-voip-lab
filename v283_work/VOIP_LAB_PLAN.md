# VOIP Lab Plan

The VOIP Lab remains isolated from production. The first concrete PBX integration is now the existing **Yeastar S50** at `10.10.10.16`.

## v2.8.3
- Yeastar S-Series provider adapter.
- Admin-only connection test.
- API 2.0 login using MD5-hashed API password.
- PBX information query after login.
- Encrypted API password storage.
- No PBX configuration changes.
- No live calls.

## Next phases
1. Discover and map Yeastar extensions.
2. Define per-user CRM extension assignments.
3. Establish browser WebRTC/SIP architecture.
4. Integrate call events and CDR into the Call Log.
5. Add click-to-call and incoming caller identification.

The production Lead CRM remains untouched while this lab is evaluated.
