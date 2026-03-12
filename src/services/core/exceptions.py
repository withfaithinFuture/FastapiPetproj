import datetime as dt
import logging
from uuid import UUID
from fastapi import HTTPException, status


logger = logging.getLogger('app.exceptions')


def check_status(response, object_name: str, object_type: str):
    if response.status_code >= 500:
        raise UnavailableServiceError(service_name='Second_Service')

    if 400 <= response.status_code < 500:
        if response.status_code == 404:
            raise NotFoundByNameError(object_name=object_name, object_type=object_type)
        raise BadValueError(field_name='Exchange')


class CacheNotSavedError(Exception):
    pass


class NotFoundError(HTTPException):
    def __init__(self, object_id: UUID, object_type: str):
        self.object_id = object_id
        self.object_type = object_type

        logger.error(f'{self.object_type} not found: id={self.object_id}')

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with id={self.object_id} was not found",
            f"{self.object_type}_id": str(self.object_id)})


class LocalDBError(HTTPException):
    def __init__(self, object_type: str, object_id: str):
        self.object_type = object_type
        self.object_id = object_id

        logger.error(f"DB error: {self.object_type}: id - {self.object_id}")

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "local_database_error",
                "message": f"{self.object_type} saving wasn`t done. There is an error",
                f"{self.object_type.lower()}_identifier": self.object_id
            }
        )


class NotFoundByNameError(HTTPException):
    def __init__(self, object_name: str, object_type: str):
        self.object_name = object_name
        self.object_type = object_type

        logger.error(f'{self.object_type} not found: name={self.object_name}')

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with name={self.object_name} was not found",
            f"{self.object_type}_name": str(self.object_name)})


class AgeMinorError(HTTPException):
    def __init__(self, date: dt.date, object_type: str = "user"):
        self.date = date
        self.object_type = object_type

        logger.error(f'{self.object_type} is underage: birth_date={date}')

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": f"{self.object_type}_underage",
                "message": f"{self.object_type} is under 18 years old",
                f"{self.object_type}_birth_date": date.isoformat()
            }
        )


class FutureDateError(HTTPException):
    def __init__(self, date: dt.date, object_type: str = "user"):
        self.date = date
        self.object_type = object_type

        logger.error(f'{self.object_type} has future date: {date}')

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"{self.object_type}_future_date",
                "message": f"{self.object_type} date cannot be in the future",
                f"{self.object_type}_date": date.isoformat(),
                "current_date": dt.date.today().isoformat()
            }
        )


class UnavailableServiceError(HTTPException):
    def __init__(self, service_name: str):
        self.service_name = service_name

        self.error = f"{self.service_name}_is_not_responding"
        self.message = f"{self.service_name} is unavailable"

        logger.error(f'{self.service_name} is not available')

        super().__init__(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail={
            "error": self.error,
            "message": self.message})


class SagaTransactionError(HTTPException):
    def __init__(self, service_name: str):
        self.service_name = service_name

        self.error = f"{self.service_name}_saga_transaction_failed"
        self.message = f"'{self.service_name}' transaction failed"

        logger.error(f'{self.service_name} saga transaction error')

        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail={
                "error": self.error,
                "message": self.message})


class BadValueError(HTTPException):
    def __init__(self, field_name: str):
        self.field_name = field_name

        self.error = f"{self.field_name}_is_invalid"
        self.message = f"{self.field_name} has invalid value"

        logger.error(f'{self.field_name} bad value error')

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": self.error,
                "message": self.message
            }
        )
