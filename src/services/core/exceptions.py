import datetime as dt
import logging
from uuid import UUID
from fastapi import HTTPException, status


logger = logging.getLogger('app.exceptions')

class NotFoundError(HTTPException):
    def __init__(self, object_id: UUID, object_type: str):
        self.object_id = object_id
        self.object_type = object_type

        logger.warning(f'{self.object_type} not found: id={self.object_id}')

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with id={self.object_id} was not found",
            f"{self.object_type}_id": str(self.object_id)})


class AgeMinorError(HTTPException):
    def __init__(self, date: dt.date, object_type: str = "user"):
        self.date = date
        self.object_type = object_type

        logger.warning(f'{self.object_type} is underage: birth_date={date}')

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

        logger.warning(f'{self.object_type} has future date: {date}')

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"{self.object_type}_future_date",
                "message": f"{self.object_type} date cannot be in the future",
                f"{self.object_type}_date": date.isoformat(),
                "current_date": dt.date.today().isoformat()
            }
        )