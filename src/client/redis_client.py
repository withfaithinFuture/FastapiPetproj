from src.app.config import settings
import logging
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.core.exceptions import CacheNotSavedError


redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
async def get_redis():
    yield redis_client


logger_cache = logging.getLogger('services.cache')

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(1, max=3),
    retry=retry_if_exception_type((CacheNotSavedError, ConnectionError, TimeoutError)),
    reraise=True
)
async def set_cache_retry(redis: Redis, key: str, value: str, expire: int):
    await redis.set(name=key, value=value, ex=expire)
    saved_cache_check = await redis.exists(key)

    if not saved_cache_check:
        logger_cache.warning(f"Данные с ключом {key} не сохранились")
        raise CacheNotSavedError()

    logger_cache.info("Данные занесены в кеш после ретраев")