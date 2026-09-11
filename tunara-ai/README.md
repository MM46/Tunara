# Tunara AI

FastAPI boundary for the future lyrics, instrumental, singing voice, cover-art and FFmpeg pipeline.
The current endpoint accepts generation requests but intentionally does not claim to generate audio until models are configured.

Run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
