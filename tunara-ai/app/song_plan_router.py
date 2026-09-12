from fastapi import APIRouter, HTTPException

from .song_plan_models import SongPlanRequest, SongPlanResponse
from .song_planner_service import SongPlannerService

router = APIRouter(prefix="/api/song-plans", tags=["song-plans"])
service = SongPlannerService()


@router.post("", response_model=SongPlanResponse)
async def create_song_plan(
    request: SongPlanRequest,
) -> SongPlanResponse:
    try:
        plan = await service.create_plan(request)
        return SongPlanResponse(
            status="COMPLETED",
            progress=100,
            plan=plan,
        )
    except Exception as exception:
        message = str(exception).strip() or "Song planning failed"
        raise HTTPException(
            status_code=502,
            detail=message,
        ) from exception
