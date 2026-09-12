import re

from .prompt_director_models import CreativeBrief, PromptDirectorRequest


class PromptDirectorService:
    REFERENCE_PROFILES = {
        "aitana": {
            "translation": (
                "Contemporary Spanish electropop and synth-pop with bright "
                "production, emotional verses, and a large melodic chorus"
            ),
            "genre": "Pop",
            "subgenre": "Spanish electropop",
            "bpm": "112-122",
            "tone": "Minor verses with a brighter relative-major chorus",
            "instrumentation": [
                "shimmering synthesizer layers",
                "tight electronic drums",
                "warm sub bass",
                "clean electric piano",
                "restrained atmospheric pads",
            ],
        },
        "tini": {
            "translation": (
                "Contemporary Latin pop with elegant urbano rhythm, melodic "
                "hooks, polished electronic drums, and confident chorus energy"
            ),
            "genre": "Latin Pop",
            "subgenre": "Melodic urbano pop",
            "bpm": "96-116",
            "tone": "Minor-key verses with an uplifting chorus resolution",
            "instrumentation": [
                "modern Latin electronic drums",
                "deep controlled bass",
                "bright synth plucks",
                "wide atmospheric pads",
                "subtle acoustic or nylon guitar accents",
            ],
        },
    }

    def direct(self, request: PromptDirectorRequest) -> CreativeBrief:
        normalized = request.idea.lower()
        matched_profiles = [
            profile
            for name, profile in self.REFERENCE_PROFILES.items()
            if re.search(rf"\b{re.escape(name)}\b", normalized)
        ]

        if matched_profiles:
            translation = " + ".join(
                profile["translation"] for profile in matched_profiles
            )
            genre = request.genre or matched_profiles[-1]["genre"]
            subgenre = " / ".join(
                profile["subgenre"] for profile in matched_profiles
            )
            bpm_range = matched_profiles[-1]["bpm"]
            tonal_direction = matched_profiles[-1]["tone"]
            instrumentation = self._unique(
                item
                for profile in matched_profiles
                for item in profile["instrumentation"]
            )
        else:
            translation = (
                "Original contemporary production derived from broad musical "
                "attributes, without imitating a real performer or existing song"
            )
            genre = request.genre or self._infer_genre(normalized)
            subgenre = self._infer_subgenre(normalized, genre)
            bpm_range = self._bpm_for_genre(genre)
            tonal_direction = (
                "Choose a practical major or minor key that supports the lyrical theme"
            )
            instrumentation = self._instrumentation_for_genre(genre)

        theme = self._extract_theme(request.idea)
        mood = self._infer_mood(normalized)
        structure = [
            "Intro",
            "Verse 1",
            "Pre-Chorus",
            "Chorus",
            "Verse 2",
            "Bridge",
            "Final Chorus",
            "Outro",
        ]
        vocal_direction = (
            "Authorized synthetic lead voice with intimate verses, clearly "
            "articulated Spanish, a lifted chorus register, controlled vibrato, "
            "and no imitation of any real singer"
        )
        arrangement = (
            "Keep verses spacious, build tension in the pre-chorus, open the "
            "stereo image in the chorus, create a real bridge breakdown, and "
            "make the final chorus larger without filling every beat"
        )
        transitions = (
            "Use restrained risers, reverse textures, drum fills, cymbal crashes, "
            "one-beat dropouts, and automation to make section boundaries obvious"
        )
        mix = (
            "Modern stereo mix with the lead melody forward, controlled low end, "
            "dynamic section levels, headroom for vocals, and 48 kHz 24-bit stems "
            "for Logic Pro"
        )
        constraints = [
            "Do not copy an existing melody, lyric, arrangement, or recording",
            "Do not imitate or clone a real person's voice",
            "Avoid constant full-volume instrumentation",
            "Avoid unnecessary filler notes",
            "Leave clear space for the lead vocal",
            "Keep all generated outputs editable and Logic Pro compatible",
        ]

        lyrics_prompt = (
            f"Write a fully original {language_name(request.language)} song about "
            f"{theme}. Use vivid but natural language, a short memorable title, "
            "two distinct verses, a pre-chorus that increases tension, a concise "
            "repeatable chorus hook, a contrasting bridge, and a final chorus. "
            "Do not mention or imitate any real artist or existing song."
        )
        planner_prompt = (
            f"Create one coherent {genre} / {subgenre} musical plan. Target "
            f"{bpm_range} BPM. {tonal_direction}. Use the structure: "
            f"{', '.join(structure)}. The mood is {mood}. Keep chord progressions "
            "singable and repeatable, make each section dynamically distinct, and "
            "reserve frequency and rhythmic space for the vocal."
        )
        production_prompt = (
            f"Produce an original {genre} / {subgenre} track with {', '.join(instrumentation)}. "
            f"{arrangement}. {transitions}. {mix}. No vocals in the instrumental "
            "render and no references to real performers in model prompts."
        )

        return CreativeBrief(
            original_idea=request.idea,
            safe_reference_translation=translation,
            genre=genre,
            subgenre=subgenre,
            language=request.language,
            duration_seconds=request.duration_seconds,
            bpm_range=bpm_range,
            tonal_direction=tonal_direction,
            mood=mood,
            lyrical_theme=theme,
            song_structure=structure,
            instrumentation=instrumentation,
            vocal_direction=vocal_direction,
            arrangement_direction=arrangement,
            transition_direction=transitions,
            mix_direction=mix,
            negative_constraints=constraints,
            lyrics_prompt=lyrics_prompt,
            song_planner_prompt=planner_prompt,
            production_prompt=production_prompt,
        )

    def _infer_genre(self, idea: str) -> str:
        if any(term in idea for term in ("reggaeton", "reguetón", "urbano")):
            return "Latin Pop"
        if any(term in idea for term in ("electronic", "electrónica", "edm")):
            return "Electropop"
        if "rock" in idea:
            return "Pop Rock"
        if any(term in idea for term in ("ballad", "balada")):
            return "Pop Ballad"
        return "Pop"

    def _infer_subgenre(self, idea: str, genre: str) -> str:
        if any(term in idea for term in ("night", "noche", "nocturno")):
            return "Nocturnal melodic pop"
        if any(term in idea for term in ("dance", "bailar", "bailable")):
            return "Dance-pop"
        return f"Contemporary {genre.lower()}"

    def _infer_mood(self, idea: str) -> str:
        if any(term in idea for term in ("ruptura", "triste", "heartbreak")):
            return "emotional, resilient, and ultimately uplifting"
        if any(term in idea for term in ("noche", "night", "nocturno")):
            return "nocturnal, cinematic, and danceable"
        return "confident, energetic, and emotionally direct"

    def _extract_theme(self, idea: str) -> str:
        cleaned = re.sub(
            r"(?i)\b(hazme|crea|quiero|una canción|una cancion|tipo|estilo|aitana|tini|o)\b",
            " ",
            idea,
        )
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.-")
        cleaned = re.sub(r"(?i)^sobre\s+", "", cleaned).strip()
        return cleaned or "personal growth and a new beginning"

    def _bpm_for_genre(self, genre: str) -> str:
        lowered = genre.lower()
        if "ballad" in lowered or "balada" in lowered:
            return "72-92"
        if "urban" in lowered or "latin" in lowered:
            return "94-112"
        if "electro" in lowered or "dance" in lowered:
            return "116-128"
        if "rock" in lowered:
            return "112-132"
        return "104-122"

    def _instrumentation_for_genre(self, genre: str) -> list[str]:
        return [
            "focused electronic drums",
            "supportive bass",
            "one primary chord instrument",
            "one restrained pad layer",
            "one hook or arpeggio layer used only where needed",
        ]

    def _unique(self, values) -> list[str]:
        return list(dict.fromkeys(values))


def language_name(language: str) -> str:
    return language.strip() or "Spanish"
