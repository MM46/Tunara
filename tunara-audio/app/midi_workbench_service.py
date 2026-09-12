import json
import math
import os
import random
import re
import shutil
import unicodedata
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pretty_midi

from .midi_workbench_models import MidiWorkbenchRequest, MidiWorkbenchResponse


class MidiWorkbenchService:
    NOTE_NAMES = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
        "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    }
    WORD_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+")

    def __init__(self) -> None:
        self.public_base_url = os.getenv(
            "AUDIO_PUBLIC_BASE_URL",
            "http://localhost:8001",
        ).rstrip("/")
        self.output_directory = Path(
            os.getenv("MIDI_WORKBENCH_OUTPUT_DIRECTORY", "generated-workbench")
        ).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        request: MidiWorkbenchRequest,
    ) -> MidiWorkbenchResponse:
        safe_id = self._safe_id(request.song_id)
        folder_name = f"{self._slug(request.plan.title)}-MIDI-Workbench"
        work_root = self.output_directory / f".{safe_id}-work"
        package_folder = work_root / folder_name

        if work_root.exists():
            shutil.rmtree(work_root)
        package_folder.mkdir(parents=True)

        root_pc, scale = self._key_scale(request.plan.key)
        beat_seconds = 60.0 / request.plan.bpm
        rng = random.Random(request.song_id)

        project = pretty_midi.PrettyMIDI(initial_tempo=request.plan.bpm)
        vocal = pretty_midi.Instrument(program=0, name="Vocal Melody Piano")
        chords = pretty_midi.Instrument(program=4, name="Electric Piano Chords")
        bass = pretty_midi.Instrument(program=33, name="Electric Bass")
        drums = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")

        total_bars = 0
        lyric_words = self._lyric_words(request.lyrics)
        lyric_cursor = 0

        for section_index, section in enumerate(request.plan.sections):
            section_start_beat = total_bars * 4.0
            self._write_harmony(
                chords,
                bass,
                drums,
                section,
                section_start_beat,
                root_pc,
                beat_seconds,
            )

            available_words = self._words_for_section(
                lyric_words,
                lyric_cursor,
                section.rhythm_density,
                section.bars,
            )
            lyric_cursor += len(available_words)
            self._write_vocal_melody(
                project,
                vocal,
                available_words,
                section,
                section_index,
                section_start_beat,
                root_pc,
                scale,
                beat_seconds,
                rng,
            )
            total_bars += section.bars

        project.instruments.extend([vocal, chords, bass, drums])

        paths = {
            "multitrack": package_folder / "01-Composer-Multitrack.mid",
            "vocal": package_folder / "02-Vocal-Melody-Piano.mid",
            "chords": package_folder / "03-Chords.mid",
            "bass": package_folder / "04-Bass.mid",
            "drums": package_folder / "05-Drums.mid",
            "plan": package_folder / "06-Song-Plan.json",
            "lyrics": package_folder / "07-Lyrics.txt",
        }

        project.write(str(paths["multitrack"]))
        self._write_single(request.plan.bpm, vocal, project.lyrics, paths["vocal"])
        self._write_single(request.plan.bpm, chords, [], paths["chords"])
        self._write_single(request.plan.bpm, bass, [], paths["bass"])
        self._write_single(request.plan.bpm, drums, [], paths["drums"])
        paths["plan"].write_text(
            json.dumps(request.plan.model_dump(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths["lyrics"].write_text(request.lyrics.strip() + "\n", encoding="utf-8")

        archive_path = self.output_directory / f"{safe_id}-midi-workbench.zip"
        with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
            for file_path in package_folder.iterdir():
                archive.write(file_path, f"{folder_name}/{file_path.name}")

        published_folder = self.output_directory / safe_id
        if published_folder.exists():
            shutil.rmtree(published_folder)
        shutil.move(str(package_folder), str(published_folder))
        shutil.rmtree(work_root)

        duration_seconds = total_bars * 4.0 * beat_seconds
        base = f"{self.public_base_url}/workbench/{safe_id}"

        return MidiWorkbenchResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            package_url=(
                f"{self.public_base_url}/workbench/"
                f"{archive_path.name}"
            ),
            multitrack_midi_url=f"{base}/01-Composer-Multitrack.mid",
            vocal_melody_midi_url=f"{base}/02-Vocal-Melody-Piano.mid",
            chords_midi_url=f"{base}/03-Chords.mid",
            bass_midi_url=f"{base}/04-Bass.mid",
            drums_midi_url=f"{base}/05-Drums.mid",
            duration_seconds=round(duration_seconds, 3),
        )

    def _write_harmony(
        self,
        chords,
        bass,
        drums,
        section,
        start_beat,
        root_pc,
        beat_seconds,
    ) -> None:
        for bar in range(section.bars):
            chord_name = section.chords[bar % len(section.chords)]
            chord_root, intervals = self._chord(chord_name, root_pc)
            bar_start = (start_beat + bar * 4.0) * beat_seconds
            bar_end = bar_start + 3.85 * beat_seconds
            octave_root = 48 + chord_root

            for interval in intervals:
                chords.notes.append(
                    pretty_midi.Note(
                        velocity=72 if section.energy == "high" else 62,
                        pitch=octave_root + interval,
                        start=bar_start,
                        end=bar_end,
                    )
                )

            bass_offsets = (
                (0.0, 1.5, 2.0, 3.5)
                if section.energy == "high"
                else (0.0, 2.0)
            )
            for offset in bass_offsets:
                note_start = bar_start + offset * beat_seconds
                bass.notes.append(
                    pretty_midi.Note(
                        velocity=88,
                        pitch=36 + chord_root,
                        start=note_start,
                        end=note_start + 0.72 * beat_seconds,
                    )
                )

            self._write_drum_bar(
                drums,
                section.energy,
                bar_start,
                beat_seconds,
            )

    def _write_vocal_melody(
        self,
        project,
        vocal,
        words,
        section,
        section_index,
        start_beat,
        root_pc,
        scale,
        beat_seconds,
        rng,
    ) -> None:
        if not words:
            return

        register_center = {
            "low": 57,
            "middle": 62,
            "high": 67,
        }[section.vocal_register]
        motif = self._motif(section_index, section.energy)
        phrase_capacity = 8
        phrase_gap = 1.0 if section.rhythm_density == "sparse" else 0.5
        note_step = {
            "sparse": 1.0,
            "balanced": 0.75,
            "dense": 0.5,
        }[section.rhythm_density]
        section_end = start_beat + section.bars * 4.0
        cursor = start_beat + 0.5
        previous_pitch = register_center

        for index, word in enumerate(words):
            if index and index % phrase_capacity == 0:
                cursor = math.ceil(cursor / 4.0) * 4.0 + phrase_gap

            if cursor + note_step > section_end:
                break

            scale_degree = motif[index % len(motif)]
            pitch_class = (root_pc + scale[scale_degree % len(scale)]) % 12
            candidates = [
                pitch
                for pitch in range(register_center - 8, register_center + 9)
                if pitch % 12 == pitch_class
            ]
            pitch = min(candidates, key=lambda value: abs(value - previous_pitch))

            if section.energy == "high" and index % phrase_capacity in {4, 5}:
                pitch = min(79, pitch + rng.choice((2, 3)))

            duration_beats = note_step * (
                1.35 if index % phrase_capacity == phrase_capacity - 1 else 0.82
            )
            start_seconds = cursor * beat_seconds
            end_seconds = (cursor + duration_beats) * beat_seconds
            note = pretty_midi.Note(
                velocity=105 if section.energy == "high" else 88,
                pitch=pitch,
                start=start_seconds,
                end=end_seconds,
            )
            vocal.notes.append(note)
            project.lyrics.append(pretty_midi.Lyric(word, start_seconds))
            previous_pitch = pitch
            cursor += note_step

    def _write_drum_bar(self, drums, energy, start, beat_seconds) -> None:
        hat_divisions = 8 if energy != "low" else 4
        for step in range(hat_divisions):
            note_start = start + step * (4.0 * beat_seconds / hat_divisions)
            drums.notes.append(
                pretty_midi.Note(55, 42, note_start, note_start + 0.05)
            )

        for beat in range(4):
            note_start = start + beat * beat_seconds
            if beat in {0, 2} or energy == "high":
                drums.notes.append(
                    pretty_midi.Note(105, 36, note_start, note_start + 0.08)
                )
            if beat in {1, 3}:
                drums.notes.append(
                    pretty_midi.Note(100, 38, note_start, note_start + 0.08)
                )

    def _words_for_section(self, words, cursor, density, bars):
        capacity_per_bar = {
            "sparse": 3,
            "balanced": 4,
            "dense": 5,
        }[density]
        capacity = bars * capacity_per_bar
        if not words:
            return []
        selected = words[cursor:cursor + capacity]
        if selected:
            return selected
        return words[:capacity]

    def _motif(self, section_index, energy):
        if energy == "high":
            return (0, 2, 4, 3, 4, 2, 1, 0)
        variants = (
            (0, 1, 2, 1, 0, 2, 1, 0),
            (0, 2, 1, 3, 2, 1, 0, 0),
        )
        return variants[section_index % len(variants)]

    def _lyric_words(self, lyrics):
        return [word.lower() for word in self.WORD_PATTERN.findall(lyrics)]

    def _key_scale(self, key):
        note_name, mode = key.split()
        root = self.NOTE_NAMES[note_name]
        scale = (
            (0, 2, 3, 5, 7, 8, 10)
            if mode == "minor"
            else (0, 2, 4, 5, 7, 9, 11)
        )
        return root, scale

    def _chord(self, chord_name, fallback_root):
        match = re.match(r"^([A-G](?:#|b)?)(.*)$", chord_name)
        if not match:
            return fallback_root, (0, 4, 7)
        root = self.NOTE_NAMES.get(match.group(1), fallback_root)
        quality = match.group(2)
        if "dim" in quality:
            intervals = (0, 3, 6)
        elif quality.startswith("m") and not quality.startswith("maj"):
            intervals = (0, 3, 7)
        else:
            intervals = (0, 4, 7)
        if "7" in quality:
            intervals = intervals + ((10 if not quality.startswith("maj") else 11),)
        return root, intervals

    def _write_single(self, bpm, instrument, lyrics, path):
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        midi.instruments.append(instrument)
        midi.lyrics.extend(lyrics)
        midi.write(str(path))

    def _safe_id(self, value):
        return "".join(
            character
            for character in value
            if character.isalnum() or character in {"-", "_"}
        )

    def _slug(self, value):
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        return (
            re.sub(r"[^A-Za-z0-9]+", "-", ascii_value)
            .strip("-")[:80]
            or "Tunara-Song"
        )
