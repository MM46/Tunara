import math
import os
import random
import re
from pathlib import Path

import pretty_midi

from .schemas import VocalMelodyRequest, VocalMelodyResponse


class VocalMelodyService:
    SECTION_PATTERN = re.compile(r"^\s*\[[^]]+]\s*$")
    WORD_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+")
    VOWEL_GROUP_PATTERN = re.compile(
        r"[aeiouáéíóúü]+",
        re.IGNORECASE,
    )

    GENRE_SETTINGS = {
        "pop": {"bpm": 112, "root": 60, "scale": [0, 2, 4, 7, 9]},
        "rock": {"bpm": 124, "root": 57, "scale": [0, 2, 3, 5, 7, 10]},
        "edm": {"bpm": 128, "root": 60, "scale": [0, 2, 3, 5, 7, 8, 10]},
        "hip hop": {"bpm": 92, "root": 58, "scale": [0, 3, 5, 7, 10]},
        "country": {"bpm": 104, "root": 55, "scale": [0, 2, 4, 7, 9]},
        "cinematic": {"bpm": 84, "root": 60, "scale": [0, 2, 3, 5, 7, 8, 11]},
    }

    def __init__(self) -> None:
        self.public_base_url = os.getenv(
            "AUDIO_PUBLIC_BASE_URL",
            "http://localhost:8001",
        ).rstrip("/")
        self.output_directory = Path(
            os.getenv("MIDI_OUTPUT_DIRECTORY", "generated-midi")
        ).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        request: VocalMelodyRequest,
    ) -> VocalMelodyResponse:
        settings = self._genre_settings(request.genre)
        lyric_units = self._extract_lyric_units(request.lyrics)

        if not lyric_units:
            raise RuntimeError("No singable lyric units were found")

        midi = pretty_midi.PrettyMIDI(
            initial_tempo=settings["bpm"]
        )
        vocal = pretty_midi.Instrument(
            program=pretty_midi.instrument_name_to_program("Voice Oohs"),
            name="Tunara Vocal Guide",
        )

        target_duration = float(request.duration_seconds)
        seconds_per_beat = 60.0 / settings["bpm"]
        minimum_note_duration = seconds_per_beat / 2.0
        maximum_units = max(1, math.floor(target_duration / minimum_note_duration))
        units = lyric_units[:maximum_units]
        note_duration = max(
            minimum_note_duration,
            target_duration / max(len(units), 1),
        )
        note_duration = min(note_duration, seconds_per_beat * 2.0)

        random_generator = random.Random(request.song_id)
        current_time = 0.0
        previous_pitch = settings["root"]

        for index, unit in enumerate(units):
            if current_time >= target_duration:
                break

            pitch = self._choose_pitch(
                settings,
                previous_pitch,
                index,
                random_generator,
            )
            end_time = min(
                target_duration,
                current_time + note_duration,
            )

            note = pretty_midi.Note(
                velocity=self._velocity(index),
                pitch=pitch,
                start=current_time,
                end=end_time,
            )
            vocal.notes.append(note)
            midi.lyrics.append(
                pretty_midi.Lyric(text=unit, time=current_time)
            )

            previous_pitch = pitch
            current_time = end_time

        if not vocal.notes:
            raise RuntimeError("Unable to generate vocal melody notes")

        midi.instruments.append(vocal)
        safe_song_id = self._safe_song_id(request.song_id)
        output_path = self.output_directory / f"{safe_song_id}-vocal.mid"
        midi.write(str(output_path))

        return VocalMelodyResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            midi_url=f"{self.public_base_url}/midi/{output_path.name}",
            bpm=settings["bpm"],
            note_count=len(vocal.notes),
            generated_duration_seconds=round(vocal.notes[-1].end, 3),
        )

    def _extract_lyric_units(self, lyrics: str) -> list[str]:
        units: list[str] = []

        for line in lyrics.splitlines():
            cleaned_line = line.strip()
            if not cleaned_line or self.SECTION_PATTERN.match(cleaned_line):
                continue

            for word in self.WORD_PATTERN.findall(cleaned_line):
                syllable_count = max(
                    1,
                    len(self.VOWEL_GROUP_PATTERN.findall(word)),
                )
                units.extend(self._split_word(word, syllable_count))

        return units

    def _split_word(self, word: str, syllable_count: int) -> list[str]:
        if syllable_count <= 1 or len(word) <= 3:
            return [word]

        chunk_size = max(2, math.ceil(len(word) / syllable_count))
        chunks = [
            word[index:index + chunk_size]
            for index in range(0, len(word), chunk_size)
        ]
        return [chunk for chunk in chunks if chunk]

    def _genre_settings(self, genre: str) -> dict[str, int | list[int]]:
        normalized_genre = genre.strip().lower()
        return self.GENRE_SETTINGS.get(
            normalized_genre,
            self.GENRE_SETTINGS["pop"],
        )

    def _choose_pitch(
        self,
        settings: dict[str, int | list[int]],
        previous_pitch: int,
        index: int,
        random_generator: random.Random,
    ) -> int:
        root = int(settings["root"])
        scale = list(settings["scale"])
        candidates = [
            root + interval + octave
            for octave in (-12, 0, 12)
            for interval in scale
            if 48 <= root + interval + octave <= 76
        ]

        nearby = [
            pitch
            for pitch in candidates
            if abs(pitch - previous_pitch) <= 5
        ]
        pool = nearby or candidates

        if index % 8 == 0:
            return min(pool, key=lambda pitch: abs(pitch - root))

        return random_generator.choice(pool)

    def _velocity(self, index: int) -> int:
        return 96 if index % 8 in {0, 4} else 84

    def _safe_song_id(self, song_id: str) -> str:
        return "".join(
            character
            for character in song_id
            if character.isalnum() or character in {"-", "_"}
        )
