# Lead CRM — VOIP Lab Build v2.10.2

> **Separate testing build. Do not use this package to upgrade the production Lead CRM.**

## Purpose
This build replaces the VoIP.ms adapter with a **Yeastar S-Series adapter** for the VOIP Lab. It connects to the existing Yeastar S50 PBX over its local API. No Yeastar software/PBX is installed on the CRM server.

## Lab topology
- CRM/VOIP Lab: `10.10.11.225`
- Existing Yeastar S50: `10.10.10.16`
- VOIP Lab application: `/opt/leadcrm-voip-lab`
- Linux user: `leadcrm-voip-lab`
- PostgreSQL database: `leadcrm_voip_lab`
- PostgreSQL role: `leadcrm_voip_lab`
- Backend service: `leadcrm-voip-lab-backend.service`
- Backend port: `8100`
- Nginx site: `leadcrm-voip-lab`

## Yeastar integration
Settings → VOIP provides:
- Yeastar S-Series provider selection
- PBX host/IP and SIP port
- Yeastar API protocol, port and API version
- API username/password with encrypted password storage
- Optional TLS certificate verification
- API connection test

The adapter logs in to the Yeastar S-Series API, receives an API token, and queries PBX information. Yeastar documents API 2.0 for S-Series PBXs and supports S50 firmware 30.5.0.30 or later. The default HTTPS API port is 8088. API passwords are MD5-hashed when requesting the API token.

The lab now supports server-side PBX-controlled click-to-call for mapped CRM users. It does not enable browser WebRTC/SIP media or modify PBX configuration.

## Yeastar preparation
On the S50, enable API access under the PBX API settings and create API credentials. For API 2.0, use the PBX API username/password and API version `2.0.0`. If the PBX uses its default HTTPS web/API port, use `8088`.

## Installation
Run on the dedicated Ubuntu 22.04 test server:

```bash
sudo bash deploy/install_ubuntu22.sh
```

For an existing VOIP Lab installation, use:

```bash
sudo bash deploy/upgrade_ubuntu22.sh
```

Then configure the Nginx hostname/IP and HTTPS as appropriate.

## Scope roadmap
1. v2.8.5 — Yeastar S-Series API connectivity test.
2. v2.9.0 — Yeastar extension discovery and per-user extension mapping.
3. v2.10.0 — server-side PBX click-to-call.
4. v2.10.2 — click-to-call mapping unassignment and lead phone clearing hotfix.
4. Next — call events/CDR integration with the CRM Call Log.
5. Next — browser WebRTC/SIP calling only after PBX-controlled calling is stable.

## v2.9 Extension Integration

This lab milestone connects to the existing Yeastar S-Series PBX and discovers extensions through the Yeastar API 2.0 `extension/query` endpoint. It displays extension number, caller ID name, type, and current status, and allows a Super Admin or Site Admin to map one extension to one active CRM user.

The CRM stores only the provider, CRM user ID, extension number, and mapping state. Yeastar SIP registration passwords, login passwords, voicemail secrets, and other detailed extension credentials are not stored or returned by the extension discovery endpoint.

This milestone does not place calls, change extension settings on the PBX, enable browser calling, or implement WebRTC/SIP media.


## v2.10 Click-to-Call

The v2.10 lab milestone adds provider-neutral click-to-call at the CRM API layer. A logged-in CRM user can initiate a call from an accessible lead when that user has an active Yeastar extension mapping. The server reads the lead phone number, validates it, authenticates to the Yeastar S-Series API, and calls `POST /api/v2.0.0/call/dial` with the mapped extension as caller and the lead phone as callee. Yeastar returns a call ID for the initiated call.

The browser never receives the Yeastar API token or credentials, and the caller extension cannot be chosen by the browser. Call initiation is recorded in the CRM audit log. The lab does not yet implement browser WebRTC/SIP media, inbound call popups, CDR synchronization, or call recording.
