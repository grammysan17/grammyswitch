# Mac build — Vectorworks 2026 plugin

## Prerequisites

- macOS with Xcode
- Vectorworks 2026 installed
- Vectorworks SDK (https://github.com/Vectorworks/developer-sdk)
- Optional Partner satellite credentials for encrypted / distributable `.vwlibrary` — see `docs/credentials.md`

## Steps (outline)

1. Set `VW_SDK` to the unpacked SDK root (CMake/Xcode user setting).
2. Open or generate an Xcode project targeting a **bundle / vwlibrary** product.
3. Add `plugin/src/*.cpp` and headers; link VW SDK frameworks as required by SDK examples.
4. Embed or install `plugin/python/*.py` where the plugin can invoke helpers (path TBD per SDK sample).
5. Build Release for Apple Silicon / Intel as needed.
6. Copy the product into Vectorworks Plug-Ins (or use SDK install target).
7. Launch VW → menu command **Start Voice Bridge** (wired in skeleton TODOs) → socket appears → run bridge client.

## Environment

```bash
export VW_SDK=/path/to/VectorworksSDK
# Never commit Partner .vst credentials
```

## Verification

1. `get_document_info` round-trip from `python -m bridge.client get_document_info`
2. `create_line` with inches coords; confirm geometry in active doc
3. Confirm socket file mode is `0600`

## TODOs marked in source

Search for `VW_SDK` and `TODO` in `plugin/src/`. Do not add arbitrary script execution APIs.
