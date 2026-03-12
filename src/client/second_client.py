import os
import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception, retry_if_exception_type
from src.services.core.exceptions import UnavailableServiceError, NotFoundError, BadValueError, NotFoundByNameError, \
    check_status
from src.services.schemas.exchange_schemas import SecondServiceValidationSchema


second_service_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))

class SecondClient:

    BASE_SECOND_SERVICE_URL = os.getenv('BASE_SECOND_SERVICE_URL')

    def __init__(self):
        self.client = httpx.AsyncClient()


    @second_service_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def get_additional_info(self, exchange_name: str) -> SecondServiceValidationSchema:
        endpoint_url = f"{self.BASE_SECOND_SERVICE_URL}exchange/{exchange_name}"

        try:
            response = await self.client.get(url=endpoint_url)
        except httpx.RequestError:
            raise UnavailableServiceError(service_name='Second_Service')

        check_status(response=response, object_name=exchange_name, object_type='Second_Service')

        data = ujson.loads(response.text)

        return SecondServiceValidationSchema.model_validate(data)


    @second_service_breaker
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def create_additional_info(self, exchange_name: str) -> SecondServiceValidationSchema:
        endpoint_url = f"{self.BASE_SECOND_SERVICE_URL}exchange/{exchange_name}"

        response = await self.client.post(url=endpoint_url)
        check_status(response=response, object_name=exchange_name, object_type='Second_Service')

        data = ujson.loads(response.text)

        return SecondServiceValidationSchema.model_validate(data)