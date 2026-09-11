import math
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path

import pretty_midi

from .schemas import VocalMelodyRequest, VocalMelodyResponse


@dataclass(frozen=True)
class GenreProfile:
    bpm: int
    root: int
    scale: tuple[int, ...]
    progression: tuple[int, ...]
    bass_pattern: tuple[float, ...]
    drum_style: str


class ComposerV2Service:
    SECTION_PATTERN = re.compile(r"^\s*\[([^]]+)]\s*$")
    WORD_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+")
    VOWELS = "aeiouáéíóúüAEIOUÁÉÍÓÚÜ"

    PROFILES = {
        "pop": GenreProfile(112, 60, (0, 2, 4, 5, 7, 9, 11), (0, 5, 3, 4), (0.0, 2.0), "pop"),
        "rock": GenreProfile(124, 57, (0, 2, 3, 5, 7, 8, 10), (0, 5, 6, 3), (0.0, 1.5, 2.0, 3.5), "rock"),
        "edm": GenreProfile(128, 60, (0, 2, 3, 5, 7, 8, 10), (0, 5, 3, 6), (0.0, 1.0, 2.0, 3.0), "edm"),
        "hip hop": GenreProfile(92, 58, (0, 3, 5, 7, 10), (0, 3, 5, 4), (0.0, 2.5), "hiphop"),
        "country": GenreProfile(104, 55, (0, 2, 4, 5, 7, 9, 11), (0, 3, 4, 0), (0.0, 2.0), "country"),
        "cinematic": GenreProfile(84, 60, (0, 2, 3, 5, 7, 8, 11), (0, 5, 3, 6), (0.0, 2.0), "cinematic"),
    }

    SECTION_BARS = {
        "intro": 4,
        "verse": 8,
        "pre": 4,
        "chorus": 8,
        "bridge": 4,
        "outro": 4,
    }

    def __init__(self) -> None:
        self.public_base_url = os.getenv("AUDIO_PUBLIC_BASE_URL", "http://localhost:8001").rstrip("/")
        self.output_directory = Path(os.getenv("MIDI_OUTPUT_DIRECTORY", "generated-midi")).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    async def generate(self, request: VocalMelodyRequest) -> VocalMelodyResponse:
        profile = self.PROFILES.get(request.genre.strip().lower(), self.PROFILES["pop"])
        sections = self._parse_sections(request.lyrics)
        song_id = self._safe(request.song_id)
        seed = random.Random(request.song_id)

        master = pretty_midi.PrettyMIDI(initial_tempo=profile.bpm)
        vocal = pretty_midi.Instrument(program=53, name="Vocal Melody Guide")
        chords = pretty_midi.Instrument(program=0, name="Chords")
        bass = pretty_midi.Instrument(program=33, name="Bass")
        drums = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")

        seconds_per_beat = 60.0 / profile.bpm
        bar_seconds = seconds_per_beat * 4.0
        current_bar = 0
        previous_pitch = profile.root + 12
        vocal_note_count = 0

        for section_index, (section_name, text) in enumerate(sections):
            family = self._section_family(section_name)
            bars = self.SECTION_BARS[family]
            start_time = current_bar * bar_seconds
            self._write_harmony(chords, bass, drums, profile, start_time, bars, bar_seconds)

            syllables = self._syllables(text)
            if syllables:
                motif = self._motif(profile, family, seed)
                phrase_slots = self._phrase_slots(family, bars)
                for index, syllable in enumerate(syllables[:len(phrase_slots)]):
                    beat, beats_long = phrase_slots[index]
                    note_start = start_time + beat * seconds_per_beat
                    note_end = note_start + beats_long * seconds_per_beat * 0.88
                    degree = motif[index % len(motif)]
                    pitch = self._nearest_pitch(profile, degree, previous_pitch, family)
                    velocity = 104 if family == "chorus" else 88
                    vocal.notes.append(pretty_midi.Note(velocity, pitch, note_start, note_end))
                    master.lyrics.append(pretty_midi.Lyric(syllable, note_start))
                    previous_pitch = pitch
                    vocal_note_count += 1

            current_bar += bars
            if current_bar * bar_seconds >= request.duration_seconds:
                break

        master.instruments.extend([vocal, chords, bass, drums])
        multitrack_path = self.output_directory / f"{song_id}-composer-v2.mid"
        vocal_path = self.output_directory / f"{song_id}-vocal.mid"
        chords_path = self.output_directory / f"{song_id}-chords.mid"
        bass_path = self.output_directory / f"{song_id}-bass.mid"
        drums_path = self.output_directory / f"{song_id}-drums.mid"

        master.write(str(multitrack_path))
        self._write_single(profile.bpm, vocal, master.lyrics, vocal_path)
        self._write_single(profile.bpm, chords, [], chords_path)
        self._write_single(profile.bpm, bass, [], bass_path)
        self._write_single(profile.bpm, drums, [], drums_path)

        duration = min(master.get_end_time(), float(request.duration_seconds))
        return VocalMelodyResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            midi_url=f"{self.public_base_url}/midi/{multitrack_path.name}",
            bpm=profile.bpm,
            note_count=vocal_note_count,
            generated_duration_seconds=round(duration, 3),
        )

    def _parse_sections(self, lyrics: str) -> list[tuple[str, str]]:
        sections: list[tuple[str, str]] = []
        name = "Verse"
        lines: list[str] = []
        for raw in lyrics.splitlines():
            match = self.SECTION_PATTERN.match(raw)
            if match:
                if lines:
                    sections.append((name, " ".join(lines)))
                name, lines = match.group(1), []
            elif raw.strip():
                lines.append(raw.strip())
        if lines:
            sections.append((name, " ".join(lines)))
        return sections or [("Verse", lyrics)]

    def _section_family(self, name: str) -> str:
        value = name.lower()
        if "chorus" in value or "coro" in value: return "chorus"
        if "bridge" in value or "puente" in value: return "bridge"
        if "intro" in value: return "intro"
        if "outro" in value: return "outro"
        if "pre" in value: return "pre"
        return "verse"

    def _syllables(self, text: str) -> list[str]:
        result: list[str] = []
        for word in self.WORD_PATTERN.findall(text):
            chunks = re.findall(r"[^aeiouáéíóúü]*[aeiouáéíóúü]+(?:[^aeiouáéíóúü](?=[^aeiouáéíóúü]|$))?", word, re.I)
            result.extend(chunks or [word])
        return result

    def _motif(self, profile: GenreProfile, family: str, rng: random.Random) -> tuple[int, ...]:
        if family == "chorus": return (0, 2, 4, 4, 3, 2, 1, 0)
        if family == "bridge": return (3, 4, 5, 4, 2, 3, 1, 0)
        variant = rng.choice(((0, 1, 2, 1, 0, 2, 1, 0), (0, 2, 1, 3, 2, 1, 0, 0)))
        return variant

    def _phrase_slots(self, family: str, bars: int) -> list[tuple[float, float]]:
        slots: list[tuple[float, float]] = []
        density = 2 if family in {"verse", "bridge"} else 3
        for bar in range(bars):
            base = bar * 4.0
            if bar % 4 == 3:
                slots.extend([(base, 1.0), (base + 1.5, 1.5)])
                continue
            for step in range(density):
                slots.append((base + step * (4.0 / density), 0.75 if density == 3 else 1.25))
        return slots

    def _nearest_pitch(self, profile: GenreProfile, degree: int, previous: int, family: str) -> int:
        scale_degree = profile.scale[degree % len(profile.scale)]
        target = profile.root + 12 + scale_degree + (5 if family == "chorus" else 0)
        candidates = [target - 12, target, target + 12]
        return min((p for p in candidates if 48 <= p <= 79), key=lambda p: abs(p - previous))

    def _write_harmony(self, chords, bass, drums, profile, start, bars, bar_seconds):
        beat_seconds = bar_seconds / 4.0
        for bar in range(bars):
            degree = profile.progression[bar % len(profile.progression)]
            root = profile.root - 12 + profile.scale[degree % len(profile.scale)]
            bar_start = start + bar * bar_seconds
            chord_pitches = (root + 12, root + 16, root + 19)
            for pitch in chord_pitches:
                chords.notes.append(pretty_midi.Note(70, pitch, bar_start, bar_start + bar_seconds * 0.92))
            for offset in profile.bass_pattern:
                note_start = bar_start + offset * beat_seconds
                bass.notes.append(pretty_midi.Note(86, root, note_start, note_start + beat_seconds * 0.8))
            self._drum_bar(drums, profile.drum_style, bar_start, beat_seconds)

    def _drum_bar(self, drums, style, start, beat):
        for eighth in range(8):
            t = start + eighth * beat / 2
            drums.notes.append(pretty_midi.Note(58, 42, t, t + 0.05))
        for beat_index in range(4):
            t = start + beat_index * beat
            kick = beat_index in ({0, 2} if style != "edm" else {0, 1, 2, 3})
            if kick: drums.notes.append(pretty_midi.Note(105, 36, t, t + 0.08))
            if beat_index in {1, 3}: drums.notes.append(pretty_midi.Note(98, 38, t, t + 0.08))

    def _write_single(self, bpm, instrument, lyrics, path):
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        midi.instruments.append(instrument)
        midi.lyrics.extend(lyrics)
        midi.write(str(path))

    def _safe(self, value: str) -> str:
        return "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_"})
