import httpx


def check_retry_error(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500

    if isinstance(exc, httpx.RequestError):
        return True

    return False