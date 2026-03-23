import httpx
import ujson
from aiobreaker import CircuitBreaker
from datetime import timedelta
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.client.utils import check_status
from src.services.core.exceptions import UnavailableServiceError
from src.services.schemas.exchange_schemas import SecondServiceValidationSchema
from src.app.config import Settings


class SecondClient:

    SERVICE_NAME = Settings.SERVICE_NAME

    def __init__(self):
        self.settings = Settings()
        self.client = httpx.AsyncClient(base_url=self.settings.base_second_service_url, timeout=self.settings.base_second_service_timeout)
        self.breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=15))
        self.get_additional_info = self.breaker(self.get_additional_info)
        self.create_additional_info = self.breaker(self.create_additional_info)
        self.delete_additional_info = self.breaker(self.delete_additional_info)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def get_additional_info(self, exchange_name: str) -> SecondServiceValidationSchema:
        endpoint_url = f"/exchange/{exchange_name}"

        response = await self.client.get(url=endpoint_url)
        check_status(response=response, object_name=exchange_name, object_type=self.SERVICE_NAME)

        return ujson.loads(response.text)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def create_additional_info(self, exchange_name: str) -> SecondServiceValidationSchema:
        endpoint_url = f"/exchange/{exchange_name}"

        response = await self.client.post(url=endpoint_url)
        check_status(response=response, object_name=exchange_name, object_type=self.SERVICE_NAME)

        return ujson.loads(response.text)


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=5),
        retry=retry_if_exception_type(UnavailableServiceError),
        reraise=True
    )
    async def delete_additional_info(self, exchange_name: str):
        endpoint_url = f"/exchange/{exchange_name}"

        response = await self.client.delete(url=endpoint_url)

        if response.status_code == 404:
            return True

        check_status(response=response, object_name=exchange_name, object_type=self.SERVICE_NAME)

        return True
