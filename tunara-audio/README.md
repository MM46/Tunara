# Tunara Audio

Native Apple Silicon service for MusicGen through MLX and vocal melody guide generation.

Available endpoints:

- `GET /health`
- `POST /api/instrumentals`
- `POST /api/vocal-melodies`
- `GET /audio/{file}.wav`
- `GET /midi/{file}.mid`

The MIDI melody is a deterministic development guide derived from the lyrics, genre, and requested duration. It is not yet a sung vocal performance. The next stage sends this guide to a singing synthesizer.
