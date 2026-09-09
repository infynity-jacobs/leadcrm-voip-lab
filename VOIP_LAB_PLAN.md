# VOIP Lab Plan

This build is intentionally isolated from production and provider-neutral.

## Current build
- VOIP settings under Settings.
- Provider/system type selection.
- PBX/SIP host, port, WebSocket, realm and STUN/TURN fields.
- Extension mode selection.
- No vendor adapter.
- No live calling.

## Later phases
1. Select the first provider integration based on lab testing.
2. Add per-user extension/credential storage with encryption.
3. Add browser softphone and click-to-call.
4. Feed call events into the existing Call Log.
5. Add incoming caller identification, call outcomes and follow-up automation.

The production Lead CRM remains untouched while this lab is evaluated.
