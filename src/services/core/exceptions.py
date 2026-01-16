from uuid import UUID
from fastapi import HTTPException


class ValidationError(HTTPException):
    def __init__(self, object_id: UUID, object_type: str):
        self.object_id = object_id
        self.object_type = object_type
        super().__init__(status_code=404, detail={{
            "error": f"{self.object_type}_not_found",
            "message": f"{self.object_type} with id={self.object_id} was not found",
            f"{self.object_type}_id": str(self.object_id)}})