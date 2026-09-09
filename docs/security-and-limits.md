# Security and limits

See root `SECURITY.md` for the authoritative policy.

Implementation enforces:

- CLI refuses trace generation for `n > 64` (viz cap)
- CLI refuses inputs above `kMaxArrayCli` (100000)
- Trace emitter hard-caps event count (5000)
- Public viz loads **trusted canned traces only**
- No user native-code execution path exists

No credentials, personal paths, or secrets are embedded in source.
