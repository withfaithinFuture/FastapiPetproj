import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_exponential_jitter
from src.services.core.exceptions import Server500Error, UnavailableServiceError
from src.services.schemas.exchange_schemas import SecondServiceValidationSchema


second_service_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))

class SecondClientService:

    BASE_URL = 'http://127.0.0.1:8001/'

    def __init__(self):
        self.client = httpx.AsyncClient()


    @second_service_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, Server500Error)),
        reraise=True
    )
    async def get_additional_info(self, exchange_name: str) -> SecondServiceValidationSchema:
        endpoint_url = f"{self.BASE_URL}exchange/{exchange_name}"

        response = await self.client.get(url=endpoint_url)
        if response.status_code >= 500:
            raise Server500Error('Second_service', status_code=response.status_code)

        elif response.status_code >= 400:
            raise UnavailableServiceError(exchange_name)

        data = response.json()

        return SecondServiceValidationSchema.model_validate(data)

