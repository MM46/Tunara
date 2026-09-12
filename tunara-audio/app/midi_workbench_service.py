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
            "AUDIO_PUBLIC_BASE_URL", "http://localhost:8001"
        ).rstrip("/")
        self.output_directory = Path(
            os.getenv("MIDI_WORKBENCH_OUTPUT_DIRECTORY", "generated-workbench")
        ).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    async def generate(self, request: MidiWorkbenchRequest) -> MidiWorkbenchResponse:
        safe_id = self._safe_id(request.song_id)
        folder_name = f"{self._slug(request.plan.title)}-Arrangement-Workbench"
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
        pads = pretty_midi.Instrument(program=89, name="Warm Pads")
        arpeggio = pretty_midi.Instrument(program=81, name="Synth Arpeggio")
        transitions = pretty_midi.Instrument(program=0, is_drum=True, name="Transitions")
        counter = pretty_midi.Instrument(program=80, name="Chorus Counter Melody")

        total_bars = 0
        lyric_words = self._lyric_words(request.lyrics)
        lyric_cursor = 0

        for section_index, section in enumerate(request.plan.sections):
            start_beat = total_bars * 4.0
            project.text_events.append(
                pretty_midi.Text(text=section.name, time=start_beat * beat_seconds)
            )
            self._arrange_section(
                chords, bass, drums, pads, arpeggio, transitions, counter,
                section, section_index, start_beat, root_pc,
                beat_seconds, rng,
            )
            words = self._words_for_section(
                lyric_words, lyric_cursor, section.rhythm_density, section.bars
            )
            lyric_cursor += len(words)
            self._write_vocal(
                project, vocal, words, section, section_index,
                start_beat, root_pc, scale, beat_seconds, rng,
            )
            total_bars += section.bars

        project.instruments.extend(
            [vocal, chords, bass, drums, pads, arpeggio, transitions, counter]
        )

        paths = {
            "multi": package_folder / "01-Composer-Multitrack.mid",
            "vocal": package_folder / "02-Vocal-Melody-Piano.mid",
            "chords": package_folder / "03-Chords.mid",
            "bass": package_folder / "04-Bass.mid",
            "drums": package_folder / "05-Drums.mid",
            "pads": package_folder / "06-Pads.mid",
            "arp": package_folder / "07-Arpeggio.mid",
            "transitions": package_folder / "08-Transitions.mid",
            "counter": package_folder / "09-Chorus-Counter-Melody.mid",
            "plan": package_folder / "10-Song-Plan.json",
            "lyrics": package_folder / "11-Lyrics.txt",
        }
        project.write(str(paths["multi"]))
        for key, instrument in (
            ("vocal", vocal), ("chords", chords), ("bass", bass),
            ("drums", drums), ("pads", pads), ("arp", arpeggio),
            ("transitions", transitions), ("counter", counter),
        ):
            self._write_single(
                request.plan.bpm,
                instrument,
                project.lyrics if key == "vocal" else [],
                paths[key],
            )
        paths["plan"].write_text(
            json.dumps(request.plan.model_dump(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        paths["lyrics"].write_text(request.lyrics.strip() + "\n", encoding="utf-8")

        archive_path = self.output_directory / f"{safe_id}-arrangement-workbench.zip"
        with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
            for file_path in package_folder.iterdir():
                archive.write(file_path, f"{folder_name}/{file_path.name}")

        published = self.output_directory / safe_id
        if published.exists():
            shutil.rmtree(published)
        shutil.move(str(package_folder), str(published))
        shutil.rmtree(work_root)

        base = f"{self.public_base_url}/workbench/{safe_id}"
        duration = total_bars * 4.0 * beat_seconds
        return MidiWorkbenchResponse(
            song_id=request.song_id,
            status="COMPLETED",
            progress=100,
            package_url=f"{self.public_base_url}/workbench/{archive_path.name}",
            multitrack_midi_url=f"{base}/{paths['multi'].name}",
            vocal_melody_midi_url=f"{base}/{paths['vocal'].name}",
            chords_midi_url=f"{base}/{paths['chords'].name}",
            bass_midi_url=f"{base}/{paths['bass'].name}",
            drums_midi_url=f"{base}/{paths['drums'].name}",
            pads_midi_url=f"{base}/{paths['pads'].name}",
            arpeggio_midi_url=f"{base}/{paths['arp'].name}",
            transitions_midi_url=f"{base}/{paths['transitions'].name}",
            counter_melody_midi_url=f"{base}/{paths['counter'].name}",
            duration_seconds=round(duration, 3),
        )

    def _arrange_section(
        self, chords, bass, drums, pads, arpeggio, transitions, counter,
        section, section_index, start_beat, root_pc, beat_seconds, rng
    ) -> None:
        family = self._section_family(section.name)
        for bar in range(section.bars):
            chord_name = section.chords[bar % len(section.chords)]
            chord_root, intervals = self._chord(chord_name, root_pc)
            beat = start_beat + bar * 4.0
            start = beat * beat_seconds
            end = (beat + 3.85) * beat_seconds
            root_midi = 48 + chord_root

            chord_velocity = 38 if family == "intro" else 58
            if section.energy == "high":
                chord_velocity = 82
            for interval in intervals:
                chords.notes.append(
                    pretty_midi.Note(chord_velocity, root_midi + interval, start, end)
                )

            bass_pattern = ()
            if family == "bridge" and bar < max(1, section.bars // 2):
                bass_pattern = (0.0,)
            elif family not in {"intro", "outro"} or bar >= section.bars // 2:
                bass_pattern = (
                    (0.0, 1.5, 2.0, 3.5)
                    if section.energy == "high"
                    else (0.0, 2.0)
                )

            for offset in bass_pattern:
                note_start = (beat + offset) * beat_seconds
                bass.notes.append(
                    pretty_midi.Note(
                        92 if section.energy == "high" else 82,
                        36 + chord_root,
                        note_start,
                        note_start + 0.7 * beat_seconds,
                    )
                )

            if family in {"intro", "bridge", "outro"} or section.energy == "high":
                pad_start = start
                pad_end = (beat + 4.0) * beat_seconds
                for interval in intervals:
                    pads.notes.append(
                        pretty_midi.Note(48, 60 + chord_root + interval, pad_start, pad_end)
                    )

            if section.energy != "low" and family not in {"outro"}:
                arp_pattern = (0, 1, 2, 1, 0, 1, 2, 1)
                for step, index in enumerate(arp_pattern):
                    note_start = (beat + step * 0.5) * beat_seconds
                    arpeggio.notes.append(
                        pretty_midi.Note(
                            58 if section.energy == "medium" else 72,
                            60 + chord_root + intervals[index % len(intervals)],
                            note_start,
                            note_start + 0.32 * beat_seconds,
                        )
                    )

            self._drum_bar(drums, section.energy, family, start, beat_seconds, bar)

            if bar == section.bars - 1:
                self._transition_fill(
                    transitions, start, beat_seconds,
                    strong=section.energy == "high" or section_index > 0,
                )

        family = self._section_family(section.name)
        if family in {"chorus", "final_chorus"}:
            self._write_counter_melody(
                counter,
                section,
                start_beat,
                root_pc,
                beat_seconds,
            )

        first_start = start_beat * beat_seconds
        transitions.notes.append(
            pretty_midi.Note(108, 49, first_start, first_start + 0.12)
        )

    def _write_counter_melody(
        self,
        counter,
        section,
        start_beat,
        root_pc,
        beat_seconds,
    ) -> None:
        pattern = (0, 4, 7, 4)
        for bar in range(section.bars):
            chord_name = section.chords[bar % len(section.chords)]
            chord_root, _ = self._chord(chord_name, root_pc)
            for step, interval in enumerate(pattern):
                note_start = (start_beat + bar * 4.0 + step) * beat_seconds
                counter.notes.append(
                    pretty_midi.Note(
                        velocity=56 if section.name.lower().startswith("final") else 46,
                        pitch=72 + chord_root + interval,
                        start=note_start,
                        end=note_start + 0.55 * beat_seconds,
                    )
                )

    def _write_vocal(
        self, project, vocal, words, section, section_index,
        start_beat, root_pc, scale, beat_seconds, rng
    ) -> None:
        if not words:
            return
        family = self._section_family(section.name)
        center = {"low": 57, "middle": 62, "high": 67}[section.vocal_register]
        motif = (
            (0, 2, 4, 3, 4, 2, 1, 0)
            if family in {"chorus", "final_chorus"}
            else (0, 1, 2, 1, 0, 2, 1, 0)
        )
        step = {"sparse": 1.0, "balanced": 0.75, "dense": 0.5}[section.rhythm_density]
        cursor = start_beat + (2.0 if family == "intro" else 0.5)
        section_end = start_beat + section.bars * 4.0
        previous = center

        for index, word in enumerate(words):
            if index and index % 8 == 0:
                cursor = math.ceil(cursor / 4.0) * 4.0 + 0.5
            if cursor + step > section_end:
                break
            degree = motif[index % len(motif)]
            pitch_class = (root_pc + scale[degree % len(scale)]) % 12
            candidates = [
                pitch for pitch in range(center - 8, center + 10)
                if pitch % 12 == pitch_class
            ]
            pitch = min(candidates, key=lambda value: abs(value - previous))
            if family in {"chorus", "final_chorus"} and index % 8 in {4, 5}:
                pitch = min(79, pitch + rng.choice((2, 3)))
            duration = step * (1.45 if index % 8 == 7 else 0.8)
            note_start = cursor * beat_seconds
            vocal.notes.append(
                pretty_midi.Note(
                    108 if section.energy == "high" else 90,
                    pitch,
                    note_start,
                    (cursor + duration) * beat_seconds,
                )
            )
            project.lyrics.append(pretty_midi.Lyric(word, note_start))
            previous = pitch
            cursor += step

    def _drum_bar(self, drums, energy, family, start, beat_seconds, bar) -> None:
        if family == "intro" and bar < 2:
            for beat in range(4):
                note_start = start + beat * beat_seconds
                drums.notes.append(pretty_midi.Note(40, 42, note_start, note_start + 0.05))
            return
        divisions = 4 if energy == "low" else 8
        for step in range(divisions):
            note_start = start + step * 4.0 * beat_seconds / divisions
            drums.notes.append(pretty_midi.Note(52, 42, note_start, note_start + 0.05))
        for beat in range(4):
            note_start = start + beat * beat_seconds
            if beat in {0, 2} or energy == "high":
                drums.notes.append(pretty_midi.Note(104, 36, note_start, note_start + 0.08))
            if beat in {1, 3}:
                drums.notes.append(pretty_midi.Note(98, 38, note_start, note_start + 0.08))

    def _transition_fill(self, transitions, start, beat_seconds, strong) -> None:
        fill_start = start + 3.0 * beat_seconds
        for step in range(4 if strong else 2):
            point = fill_start + step * (beat_seconds / (4 if strong else 2))
            transitions.notes.append(
                pretty_midi.Note(95, 45 + (step % 3) * 2, point, point + 0.06)
            )
        transitions.notes.append(
            pretty_midi.Note(110, 57, start + 3.75 * beat_seconds, start + 3.9 * beat_seconds)
        )

    def _section_family(self, name):
        value = name.lower()
        if "final" in value and ("chorus" in value or "coro" in value): return "final_chorus"
        if "chorus" in value or "coro" in value: return "chorus"
        if "pre" in value: return "pre_chorus"
        if "bridge" in value or "puente" in value: return "bridge"
        if "intro" in value: return "intro"
        if "outro" in value: return "outro"
        return "verse"

    def _words_for_section(self, words, cursor, density, bars):
        capacity = bars * {"sparse": 3, "balanced": 4, "dense": 5}[density]
        selected = words[cursor:cursor + capacity]
        return selected if selected else words[:capacity]

    def _lyric_words(self, lyrics):
        return [word.lower() for word in self.WORD_PATTERN.findall(lyrics)]

    def _key_scale(self, key):
        note_name, mode = key.split()
        root = self.NOTE_NAMES[note_name]
        return root, ((0, 2, 3, 5, 7, 8, 10) if mode == "minor" else (0, 2, 4, 5, 7, 9, 11))

    def _chord(self, chord_name, fallback_root):
        match = re.match(r"^([A-G](?:#|b)?)(.*)$", chord_name)
        if not match:
            return fallback_root, (0, 4, 7)
        root = self.NOTE_NAMES.get(match.group(1), fallback_root)
        quality = match.group(2)
        intervals = (0, 3, 7) if quality.startswith("m") and not quality.startswith("maj") else (0, 4, 7)
        if "dim" in quality:
            intervals = (0, 3, 6)
        if "7" in quality:
            intervals += (11 if quality.startswith("maj") else 10,)
        return root, intervals

    def _write_single(self, bpm, instrument, lyrics, path):
        midi = pretty_midi.PrettyMIDI(initial_tempo=bpm)
        midi.instruments.append(instrument)
        midi.lyrics.extend(lyrics)
        midi.write(str(path))

    def _safe_id(self, value):
        return "".join(character for character in value if character.isalnum() or character in {"-", "_"})

    def _slug(self, value):
        ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^A-Za-z0-9]+", "-", ascii_value).strip("-")[:80] or "Tunara-Song"
