from fastapi import HTTPException


class ValidationError(HTTPException):
    def __init__(self, object_id, message = None):
        self.object_id = object_id
        self.message = message
        if self.message is None:
            self.message = f'Клуб с ID = {self.object_id} не найден! Введите корректный ID!'
        super().__init__(status_code=404, detail={"error": "VALIDATION_ERROR", "message": self.message})


class NothingExists(HTTPException):
    def __init__(self, object_id, message = None):
        self.object_id = object_id
        self.message = message
        if self.message is None:
            self.message = f"Футболиста или клуба с ID = {self.object_id} не существует! Введите корректный ID!"
        super().__init__(status_code=404, detail={"error": "EXISTING_ERROR", "message": self.message})



