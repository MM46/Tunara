import os

import httpx


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://host.docker.internal:11434",
        )
        self.model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2:3b",
        )
        self.timeout = float(
            os.getenv(
                "OLLAMA_TIMEOUT_SECONDS",
                "300",
            )
        )

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        generated_text = str(
            data.get("response", "")
        ).strip()

        if not generated_text:
            raise RuntimeError(
                "Ollama returned an empty response"
            )

        return generated_text