# VOIP Lab Plan

The VOIP Lab remains isolated from production. The first concrete PBX integration is now the existing **Yeastar S50** at `10.10.10.16`.

## v2.8.5
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

## v2.9 - Extension Integration

1. Authenticate to the existing Yeastar S50 using the proven TLS 1.2 / AES256-GCM-SHA384 compatibility path.
2. Query all extensions using API 2.0 `extension/query`.
3. Show extension number, name, type, and status in Settings → VOIP.
4. Map an extension to an active CRM user with one-to-one uniqueness per provider.
5. Store only the mapping metadata in the CRM; do not store Yeastar SIP credentials.
6. Leave call control and browser calling for later milestones.


## v2.10 Click-to-Call
- Use the provider-neutral adapter operation `make_call(caller, callee, autoanswer)` so Yeastar-specific API details remain isolated.
- For Yeastar S-Series API 2.0, call `POST /api/v2.0.0/call/dial?token=...` with the mapped extension as `caller`, lead phone digits as `callee`, and `autoanswer=no`.
- The CRM server, not the browser, resolves the lead phone and CRM-user extension mapping.
- Record call initiation and returned Yeastar call ID in the audit log.
- Do not expose API tokens or credentials.
- Keep WebRTC/SIP media and call-event/CDR work for later milestones.


## v2.10.2 — Click-to-Call
- Add PBX-controlled click-to-call from Lead Details.
- Resolve caller extension from the authenticated CRM user's active mapping.
- Resolve callee from the selected lead's stored phone number.
- Use Yeastar S-Series API 2.0 `call/dial` and return the PBX `callid`.
- Keep API credentials and tokens server-side.
- Audit each call initiation attempt.
- No browser SIP/WebRTC media in this milestone.
