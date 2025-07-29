# from typing import Union
# import uuid
# from src.exceptions import EntityNotFoundError
# from src.files.models.file import File


# class FileNotFoundError(EntityNotFoundError):
#     def __init__(self, file_id: Union[str, uuid.UUID]):
#         super().__init__(
#             entity=File,
#             entity_id=str(file_id),
#         )
