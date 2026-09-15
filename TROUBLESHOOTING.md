# VOIP Lab Troubleshooting

## Yeastar API test fails
1. Confirm the Yeastar S50 is reachable from the VOIP Lab server.
2. Confirm API is enabled on the PBX.
3. Confirm the API username and password match the PBX API settings.
4. Confirm API protocol/port. Default Yeastar S-Series API access is HTTPS on port 8088.
5. For a lab with a self-signed PBX certificate, leave **Verify Yeastar TLS certificate** disabled.
6. If API login fails repeatedly, stop testing until the credentials are verified; Yeastar can temporarily block an application IP after repeated failed API logins.

## Browser calling
Browser calling is not included in v2.10.2. Do not expose SIP credentials to browser JavaScript. The next phase should use a controlled SIP/WebRTC architecture.


## v2.10 Click-to-Call

If **PBX Call** fails:

1. Confirm VOIP is enabled in Settings → VOIP.
2. Confirm the active provider is Yeastar S-Series.
3. Confirm the logged-in CRM user has an active extension mapping.
4. Confirm the lead has a phone number containing dialable digits.
5. Confirm the Yeastar extension has permission to place the destination number through the PBX outbound route.
6. Check the CRM backend journal for the audit action `voip_click_to_call`.

The Yeastar S-Series API `call/dial` returns a unique `callid` when the request is accepted. The CRM records that call ID in the audit details but does not expose the Yeastar API token.
