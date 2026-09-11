import json
import re
from typing import Any

from .ollama_client import OllamaClient
from .schemas import GenerateSongRequest


class LyricsService:
    def __init__(
        self,
        ollama_client: OllamaClient,
    ) -> None:
        self.ollama_client = ollama_client

    async def generate(
        self,
        request: GenerateSongRequest,
    ) -> tuple[str, str]:
        prompt = self._build_prompt(request)

        raw_response = await self.ollama_client.generate(
            prompt
        )

        return self._parse_response(raw_response)

    def _build_prompt(
        self,
        request: GenerateSongRequest,
    ) -> str:
        return f"""
You are a professional songwriter.

Create a fully original song using these requirements:

User idea:
{request.prompt}

Genre:
{request.genre}

Language:
{request.language}

Voice style:
{request.voice}

Target duration:
{request.duration_seconds} seconds

Song requirements:

1. Write an original and memorable title.
2. Write complete original lyrics.
3. Match the requested language.
4. Match the requested genre.
5. Do not imitate or quote existing artists or songs.
6. Use this structure when appropriate:
   [Intro]
   [Verse 1]
   [Chorus]
   [Verse 2]
   [Chorus]
   [Bridge]
   [Final Chorus]
   [Outro]

Return one JSON object only.

The JSON object must contain exactly these fields:

{{
  "title": "Short song title",
  "lyrics": "Complete lyrics with line breaks"
}}

Do not include Markdown.
Do not include code fences.
Do not include explanations.
Do not include text before or after the JSON object.
""".strip()

    def _parse_response(
        self,
        raw_response: str,
    ) -> tuple[str, str]:
        cleaned_response = self._clean_response(
            raw_response
        )

        try:
            parsed_response: Any = json.loads(
                cleaned_response
            )
        except json.JSONDecodeError:
            extracted_json = self._extract_json_object(
                cleaned_response
            )

            try:
                parsed_response = json.loads(
                    extracted_json
                )
            except json.JSONDecodeError as exception:
                raise RuntimeError(
                    "Ollama did not return valid JSON. "
                    f"Response received: "
                    f"{cleaned_response[:500]}"
                ) from exception

        if not isinstance(parsed_response, dict):
            raise RuntimeError(
                "Ollama response must be a JSON object"
            )

        title = str(
            parsed_response.get("title", "")
        ).strip()

        lyrics = str(
            parsed_response.get("lyrics", "")
        ).strip()

        if not title:
            raise RuntimeError(
                "Ollama response is missing the song title"
            )

        if not lyrics:
            raise RuntimeError(
                "Ollama response is missing the song lyrics"
            )

        normalized_title = self._normalize_title(title)
        normalized_lyrics = self._normalize_lyrics(lyrics)

        return normalized_title, normalized_lyrics

    def _clean_response(
        self,
        raw_response: str,
    ) -> str:
        cleaned_response = raw_response.strip()

        cleaned_response = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned_response,
            flags=re.IGNORECASE,
        )

        cleaned_response = re.sub(
            r"\s*```$",
            "",
            cleaned_response,
        )

        return cleaned_response.strip()

    def _extract_json_object(
        self,
        response: str,
    ) -> str:
        start_index = response.find("{")
        end_index = response.rfind("}")

        if (
            start_index == -1
            or end_index == -1
            or end_index <= start_index
        ):
            raise RuntimeError(
                "Ollama response does not contain "
                "a JSON object"
            )

        return response[
            start_index:end_index + 1
        ]

    def _normalize_title(
        self,
        title: str,
    ) -> str:
        normalized_title = title.replace(
            "\n",
            " ",
        ).strip()

        normalized_title = re.sub(
            r"\s+",
            " ",
            normalized_title,
        )

        return normalized_title[:255]

    def _normalize_lyrics(
        self,
        lyrics: str,
    ) -> str:
        normalized_lyrics = lyrics.replace(
            "\\n",
            "\n",
        ).strip()

        normalized_lyrics = re.sub(
            r"\n{3,}",
            "\n\n",
            normalized_lyrics,
        )

        return normalized_lyrics