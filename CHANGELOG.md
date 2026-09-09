# Changelog

## v2.8.2 - VoIP.ms adapter lab
- Added provider-neutral VOIP adapter interface.
- Added first provider adapter: VoIP.ms.
- Added encrypted VoIP.ms SIP password and API password settings.
- Added SIP username, authentication username, DID/caller-ID, POP/server, and API username settings.
- Added an admin-only provider test endpoint using the VoIP.ms REST/JSON API.
- Added provider registration-status check through VoIP.ms `getRegistrationStatus`.
- Added DNS validation for the configured SIP POP.
- Added the missing composite uniqueness constraint to `LeadProduct` for fresh installations.
- Fixed installer schema bootstrap ordering, working directory, and application-user permissions.
- Browser WebRTC calling is intentionally not enabled yet.

## v2.8.1
- Provider-neutral VOIP lab foundation.
