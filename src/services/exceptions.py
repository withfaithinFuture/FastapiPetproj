class ValidationError(Exception):
    def __init__(self, object_id, message = None):
        self.object_id = object_id
        if message is None:
            message = f'Клуб с ID = {self.object_id} не найден! Введите корректный ID!'
        super().__init__(message)


class NothingExists(Exception):
    def __init__(self, object_id, message = None):
        self.object_id = object_id
        if message is None:
            message = f"Футболиста или клуба с ID = {self.object_id} не существует! Введите корректный ID!"
        super().__init__(message)



