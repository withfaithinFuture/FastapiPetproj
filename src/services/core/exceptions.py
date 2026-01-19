import logging
from uuid import UUID
from fastapi import HTTPException, status


logger = logging.getLogger('app.exceptions')

class NotFoundError(HTTPException):
    def __init__(self, object_id: UUID, object_type: str):
        self.object_id = object_id
        self.object_type = object_type

        logger.warning(f'{self.object_type} not found: id={self.object_id}')

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={{
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with id={self.object_id} was not found",
            f"{self.object_type}_id": str(self.object_id)}})


class InvalidEmailFormat(HTTPException):
    def __init__(self, email: str):
        self.email = email

        logger.warning(f'Invalid email format: {self.email}')

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail={
            "error": "email_invalid_format",
            "message": f"{self.email} has invalid format. Correct example: example@ya.ru"})


class InvalidEmailDomain(HTTPException):
    def __init__(self, email: str):
        self.email = email

        logger.warning(f'Invalid email domain: {self.email}')

        super().__init__(status_code=status.HTTP_400_BAD_REQUEST , detail={
            "error": "email_invalid_domain",
            "message": f"{self.email} has invalid domain. Correct domains are ('ru', 'su', 'рф', 'дети', 'москва', 'рус')"})
