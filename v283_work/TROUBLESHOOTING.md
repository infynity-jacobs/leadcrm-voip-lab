# VOIP Lab Troubleshooting

## Yeastar API test fails
1. Confirm the Yeastar S50 is reachable from the VOIP Lab server.
2. Confirm API is enabled on the PBX.
3. Confirm the API username and password match the PBX API settings.
4. Confirm API protocol/port. Default Yeastar S-Series API access is HTTPS on port 8088.
5. For a lab with a self-signed PBX certificate, leave **Verify Yeastar TLS certificate** disabled.
6. If API login fails repeatedly, stop testing until the credentials are verified; Yeastar can temporarily block an application IP after repeated failed API logins.

## Browser calling
Browser calling is not included in v2.8.3. Do not expose SIP credentials to browser JavaScript. The next phase should use a controlled SIP/WebRTC architecture.
