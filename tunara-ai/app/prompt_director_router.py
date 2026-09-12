from fastapi import APIRouter

from .prompt_director_models import (
    PromptDirectorRequest,
    PromptDirectorResponse,
)
from .prompt_director_service import PromptDirectorService

router = APIRouter(prefix="/api/prompt-director", tags=["prompt-director"])
service = PromptDirectorService()


@router.post("", response_model=PromptDirectorResponse)
async def direct_prompt(
    request: PromptDirectorRequest,
) -> PromptDirectorResponse:
    return PromptDirectorResponse(
        status="COMPLETED",
        progress=100,
        brief=service.direct(request),
    )
