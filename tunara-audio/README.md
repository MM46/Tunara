# Tunara Audio

Native Apple Silicon service for MusicGen through MLX.

Run this service from the ARM Python 3.11 environment where
`mlx-audiocraft` is installed:

```bash
cd ~/Tunara/tunara-ai
source .venv-audio/bin/activate
cd ../tunara-audio
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The development service caps generated instrumentals at 30 seconds to
keep local generation practical. This limit is configurable through
`MUSICGEN_MAX_DURATION_SECONDS`.
