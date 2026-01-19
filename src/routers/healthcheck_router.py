from fastapi import APIRouter
from src.services.schemas.healthcheck_schema import HealthcheckResponse


router = APIRouter()

@router.get('/healthcheck')
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status="ok")
