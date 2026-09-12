import re


class LyricsSanitizer:
    SECTION_ALIASES = {
        "verse": "[Verse]", "verse 1": "[Verse 1]", "verse 2": "[Verse 2]",
        "verso": "[Verse]", "verso 1": "[Verse 1]", "verso 2": "[Verse 2]",
        "pre chorus": "[Pre-Chorus]", "pre-chorus": "[Pre-Chorus]",
        "pre coro": "[Pre-Chorus]", "pre-coro": "[Pre-Chorus]", "precoro": "[Pre-Chorus]",
        "chorus": "[Chorus]", "coro": "[Chorus]",
        "final chorus": "[Final Chorus]", "coro final": "[Final Chorus]",
        "bridge": "[Bridge]", "puente": "[Bridge]",
        "outro": "[Outro]", "final": "[Outro]",
        "intro": "[Instrumental]", "instrumental intro": "[Instrumental]",
        "introduccion": "[Instrumental]", "introducción": "[Instrumental]",
        "post chorus": "[Instrumental]", "post-chorus": "[Instrumental]",
        "instrumental post chorus": "[Instrumental]",
    }
    SECTION_PATTERN = re.compile(r"^\s*\[?([^\]:]+)\]?\s*:?\s*$", re.IGNORECASE)
    WORD_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:'[A-Za-z]+)?")

    def sanitize(self, lyrics: str, duration_seconds: int | None = None) -> str:
        del duration_seconds
        normalized = lyrics.replace("\r\n", "\n").replace("\r", "\n")
        output = []
        has_instrumental = False
        for raw in normalized.splitlines():
            line = raw.strip()
            if not line:
                if output and output[-1] != "":
                    output.append("")
                continue
            section = self._section_name(line)
            if section:
                if section == "[Instrumental]":
                    has_instrumental = True
                if output and output[-1] != "":
                    output.append("")
                output.append(section)
                output.append("")
                continue
            cleaned = self._clean_line(line)
            if cleaned:
                output.append(cleaned)
        while output and output[-1] == "":
            output.pop()
        if not output:
            raise ValueError("Lyrics became empty after normalization")
        if not has_instrumental:
            output = ["[Instrumental]", ""] + output
        return "\n".join(output)

    def minimum_duration_seconds(self, lyrics: str, bpm: int = 108) -> int:
        words = self.lyric_words(lyrics)
        sections = sum(1 for line in lyrics.splitlines() if self._section_name(line))
        spoken_seconds = len(words) / 1.55
        musical_space = max(12, sections * 3)
        tempo_factor = 108 / max(70, min(160, bpm))
        return max(30, int((spoken_seconds * tempo_factor + musical_space + 9) // 10 * 10))

    def lyric_words(self, lyrics: str) -> list[str]:
        return [w.lower() for line in lyrics.splitlines() if not self._section_name(line.strip()) for w in self.WORD_PATTERN.findall(line)]

    def section_labels(self) -> set[str]:
        labels=set()
        for key in self.SECTION_ALIASES:
            labels.update(self.WORD_PATTERN.findall(key.lower()))
        return labels

    def _section_name(self, line: str) -> str | None:
        match=self.SECTION_PATTERN.match(line)
        if not match:
            return None
        key=re.sub(r"\s+", " ", match.group(1).strip().lower())
        return self.SECTION_ALIASES.get(key)

    def _clean_line(self, line: str) -> str:
        line=re.sub(r"^[\-*•]+\s*", "", line)
        line=re.sub(r"\([^)]*(instrumental|pause|silence|spoken)[^)]*\)", "", line, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", line).strip(" ,;:-")
