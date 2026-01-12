from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get('/healthcheck')
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}
