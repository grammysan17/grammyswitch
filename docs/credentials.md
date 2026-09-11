# Vectorworks 2026 plugin credentials

## Why credentials matter

For Vectorworks **2026+**, distributed **encrypted** / SDK-built plugins (`.vwlibrary`) typically require **satellite developer credentials** — a `.vst` credentials file issued via Partner / Vectorworks Developer Support (`devsupport@vectorworks.net`).

Credentials are **per major version** (2026, etc.).

## Phase 0 stance

| Mode | Credential need |
| --- | --- |
| Linux mock (`BRIDGE_MOCK=1`) | None |
| Dev-local unencrypted script / unpackaged helpers | May load with warnings; OK for spike |
| Compiled `.vwlibrary` shared beyond your machine | Plan Partner credentials before distribute |

Phase 0 plugin code under `plugin/` is a **skeleton** with `VW_SDK` TODOs — it does not ship a signed binary.

## Practical steps (Mac)

1. Join / confirm Vectorworks Partner / developer access.
2. Request 2026 satellite credentials per official docs:
   - https://github.com/Vectorworks/developer-scripting/blob/main/Common/Tasks/Info/PluginCredentials.md
3. Place the credentials file where the SDK / packaging tooling expects it (see Partner docs; never commit secrets to git).
4. Build with Xcode + VW SDK; install into VW plug-ins folder; start bridge from menu command.

## Secrets hygiene

- Do **not** commit `.vst` credential files, API keys, or cloud STT tokens.
- Use env vars / macOS Keychain for cloud STT if used in bake-off.
- Document in PRs when a change requires Partner packaging.

## References

- Developer landing: https://developer.vectorworks.net/
- SDK: https://github.com/Vectorworks/developer-sdk
- Plugin credentials (2026+): https://github.com/Vectorworks/developer-scripting/blob/main/Common/Tasks/Info/PluginCredentials.md
