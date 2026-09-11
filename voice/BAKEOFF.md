# STT bake-off matrix (Phase 0)

Run on Graham’s Mac with real PTT audio (~3–8 s utterances, architecture units).

| Backend | Offline | Latency (p50 target) | Units accuracy | Privacy | Notes |
| --- | --- | --- | --- | --- | --- |
| **apple_speech** | Often on-device | 200–600 ms | TBD | High | Native; stub on Linux |
| **whisper** (whisper.cpp / OpenAI Whisper) | Yes | Higher CPU/ANE cost | TBD | High | Quality; GPU optional |
| **cloud** | No | Often low | TBD | Lower | Flag-gated; document egress |

## Metrics to log

1. PTT release → final transcript (ms)
2. Word error on “twelve foot”, “3.6 meter”, “ten feet”
3. False finals / partial churn
4. Cost per hour if cloud

## CLI (Linux stubs)

```bash
PYTHONPATH=. python -m voice.cli --backend passthrough --text "draw a 10 foot line" --parse
PYTHONPATH=. python -m voice.cli --backend whisper --wav /path/to/sample.wav
```

## Recommendation to validate

Start with **Apple Speech or Whisper.cpp** for privacy; keep cloud behind a flag for A/B accuracy.
