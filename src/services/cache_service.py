import logging
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.core.exceptions import CacheNotSavedError


logger_cache = logging.getLogger('services.cache')

class CacheService:

    def __init__(self, redis: Redis, key: str, value: str, expire: int):
        self.redis = redis
        self.key = key
        self.value = value
        self.expire = expire


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(1, max=3),
        retry=retry_if_exception_type((CacheNotSavedError, ConnectionError, TimeoutError)),
        reraise=True
    )
    async def set_cache_retry(self, key: str, value: str, expire: int):
        await self.redis.set(key=key, value=value, ex=expire)
        saved_cache_check = await self.redis.exists(key)
        if not saved_cache_check:
            logger_cache.warning(f"Данные с ключом {key} не сохранились")
            raise CacheNotSavedError()

        logger_cache.info("Данные занесены в кеш после ретраев")