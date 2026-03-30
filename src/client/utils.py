from src.core.exceptions import UnavailableServiceError, NotFoundByNameError, ExternalClientError


def check_status(response, object_name: str, object_type: str):
    if response.status_code >= 500:
        raise UnavailableServiceError(service_name=object_name)

    if 400 <= response.status_code < 500:
        if response.status_code == 404:
            raise NotFoundByNameError(object_name=object_name, object_type=object_type)

        raise ExternalClientError(service_name=object_name, status_code=response.status_code, details=response.text)
