# Lead CRM — VOIP Lab Build v2.8.5

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

The current test does **not** place calls, modify PBX configuration, create extensions, or enable browser calling.

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
2. Next — Yeastar extension discovery and per-user extension mapping.
3. Next — SIP/WebRTC browser calling through the chosen architecture.
4. Next — call events/CDR integration with the CRM Call Log.
5. Next — click-to-call, incoming caller identification, outcomes and follow-ups.
