from typing import NotRequired, TypedDict

from pymongo.asynchronous.collection import AsyncCollection

from ..db import database


class FileDocument(TypedDict):
    name: str
    status: str
    file_path: NotRequired[str]
    result: NotRequired[str | None]
    error: NotRequired[str | None]


def create_file_document(name: str, status: str) -> FileDocument:
    return {
        "name": name,
        "status": status,
        "result": None,
        "error": None,
    }


COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]
