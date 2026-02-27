from fastapi import APIRouter, status
from src.services.schemas.healthcheck_schema import HealthcheckResponse


router = APIRouter()

@router.get('/healthcheck', status_code=status.HTTP_200_OK)
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(status = 'Service is good')
