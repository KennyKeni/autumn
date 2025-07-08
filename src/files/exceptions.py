from src.exceptions import EntityNotFoundError
from src.files.models.file import File


class FileNotFoundError(EntityNotFoundError):
    def __init__(self, file_id):
        super().__init__(
            entity=File,
            entity_id=file_id,
        )
