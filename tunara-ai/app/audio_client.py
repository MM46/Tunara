import asyncio
import json
import os
from typing import Any
from urllib.parse import quote, urlparse

import httpx


class AudioClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "ACESTEP_BASE_URL", "http://127.0.0.1:8010"
        ).rstrip("/")
        self.public_base_url = os.getenv(
            "ACESTEP_PUBLIC_BASE_URL", "http://localhost:8010"
        ).rstrip("/")
        self.tunara_audio_url = os.getenv(
            "TUNARA_AUDIO_BASE_URL", "http://127.0.0.1:8001"
        ).rstrip("/")
        self.timeout = float(os.getenv("ACESTEP_TIMEOUT_SECONDS", "1800"))
        self.poll_seconds = float(os.getenv("ACESTEP_POLL_SECONDS", "3"))
        self.model = os.getenv("ACESTEP_MODEL", "acestep-v15-turbo")
        self.lm_model = os.getenv(
            "ACESTEP_LM_MODEL", "acestep-5Hz-lm-1.7B"
        )
        self.lm_backend = os.getenv("ACESTEP_LM_BACKEND", "mlx")

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def generate_song(
        self,
        request: Any,
        lyrics: str,
        batch_size: int = 2,
    ) -> dict[str, Any]:
        payload = {
            "prompt": self._build_caption(request),
            "lyrics": lyrics,
            "thinking": True,
            "sample_mode": False,
            "use_format": False,
            "model": self.model,
            "vocal_language": self._language_code(request.language),
            "audio_duration": request.duration_seconds,
            "batch_size": batch_size,
            "audio_format": "wav",
            "inference_steps": 8,
            "guidance_scale": 1.0,
            "shift": 3.0,
            "use_random_seed": True,
            "task_type": "text2music",
            "lm_model_path": self.lm_model,
            "lm_backend": self.lm_backend,
            "allow_lm_batch": True,
            "use_tiled_decode": True,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            release = await client.post(
                f"{self.base_url}/release_task", json=payload
            )
            release.raise_for_status()
            task_id = self._find_value(release.json(), "task_id")
            if not task_id:
                raise RuntimeError(
                    f"ACE-Step did not return task_id: {release.text}"
                )

            deadline = asyncio.get_running_loop().time() + self.timeout
            while asyncio.get_running_loop().time() < deadline:
                query = await client.post(
                    f"{self.base_url}/query_result",
                    json={"task_id_list": [task_id]},
                )
                query.raise_for_status()
                item = self._find_task_item(query.json(), str(task_id))
                if item is not None:
                    status = int(item.get("status", 0))
                    results = self._decode_result(item.get("result", "[]"))
                    if status == 1:
                        references = [
                            self._result_audio_reference(result)
                            for result in results
                        ]
                        references = [value for value in references if value]
                        if not references:
                            raise RuntimeError(
                                "ACE-Step completed without audio files"
                            )
                        permanent_urls = []
                        for index, reference in enumerate(references):
                            permanent_id = (
                                request.song_id
                                if index == 0
                                else f"{request.song_id}-candidate-{index + 1}"
                            )
                            permanent_urls.append(
                                await self._persist_audio(
                                    client,
                                    permanent_id,
                                    reference,
                                )
                            )
                        metadata = results[0].get("metas", {}) or {}
                        return {
                            "task_id": str(task_id),
                            "wav_urls": permanent_urls,
                            "audio_paths": references,
                            "bpm": metadata.get("bpm"),
                            "duration": metadata.get("duration"),
                            "keyscale": metadata.get("keyscale", ""),
                            "timesignature": metadata.get("timesignature", ""),
                        }
                    if status == 2:
                        error = "ACE-Step generation failed"
                        if results:
                            error = results[0].get("error") or error
                        raise RuntimeError(str(error))
                await asyncio.sleep(self.poll_seconds)

        raise TimeoutError(
            f"ACE-Step exceeded timeout of {self.timeout} seconds"
        )

    async def _persist_audio(
        self,
        client: httpx.AsyncClient,
        song_id: str,
        reference: str,
    ) -> str:
        source_url = self._internal_audio_url(reference)
        source = await client.get(source_url)
        source.raise_for_status()

        stored = await client.post(
            f"{self.tunara_audio_url}/api/permanent-audio/{song_id}",
            files={
                "audio": (
                    "ace-step-output.wav",
                    source.content,
                    source.headers.get("content-type", "audio/wav"),
                )
            },
        )
        stored.raise_for_status()
        payload = stored.json()
        wav_url = str(payload.get("wav_url", "")).strip()
        if not wav_url:
            raise RuntimeError(
                f"Tunara Audio returned no permanent WAV URL: {stored.text}"
            )
        return wav_url

    def _build_caption(self, request: Any) -> str:
        parts = [request.prompt.strip(), request.genre.strip()]
        if request.voice.strip():
            parts.append(f"vocal style: {request.voice.strip()}")
        return ", ".join(part for part in parts if part)[:512]

    def _language_code(self, value: str) -> str:
        normalized = value.strip().lower()
        aliases = {
            "spanish": "es",
            "espanol": "es",
            "español": "es",
            "english": "en",
            "ingles": "en",
            "inglés": "en",
        }
        return aliases.get(normalized, normalized or "unknown")

    def _result_audio_reference(self, result: dict[str, Any]) -> str:
        return str(result.get("file") or result.get("wave") or "").strip()

    def _internal_audio_url(self, reference: str) -> str:
        if reference.startswith("/v1/audio?"):
            return f"{self.base_url}{reference}"
        if reference.startswith("http://") or reference.startswith("https://"):
            parsed = urlparse(reference)
            if parsed.path == "/v1/audio":
                suffix = parsed.path
                if parsed.query:
                    suffix += f"?{parsed.query}"
                return f"{self.base_url}{suffix}"
            return reference
        return f"{self.base_url}/v1/audio?path={quote(reference, safe='')}"

    def _find_value(self, value: Any, key: str) -> Any:
        if isinstance(value, dict):
            if key in value:
                return value[key]
            for child in value.values():
                found = self._find_value(child, key)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = self._find_value(child, key)
                if found is not None:
                    return found
        return None

    def _find_task_item(
        self, value: Any, task_id: str
    ) -> dict[str, Any] | None:
        if isinstance(value, dict):
            if str(value.get("task_id", "")) == task_id:
                return value
            for child in value.values():
                found = self._find_task_item(child, task_id)
                if found is not None:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = self._find_task_item(child, task_id)
                if found is not None:
                    return found
        return None

    def _decode_result(self, value: Any) -> list[dict[str, Any]]:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                return []
        if isinstance(value, dict):
            return [value]
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return []
