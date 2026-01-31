import json
from pathlib import Path

from .constants import (
    DATA_DIRECTORY,
    DEFAULT_METADATA_FILE,
    ENCODING,
    JSON_ENSURE_ASCII,
    JSON_INDENT,
    TABLE_FILE_EXTENSION,
)


def load_metadata(filepath: str = DEFAULT_METADATA_FILE) -> dict:
    """Загружает метаданные из файла."""

    try:
        with open(filepath, 'r', encoding=ENCODING) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(data: dict, filepath: str = DEFAULT_METADATA_FILE) -> None:
    """Сохраняет метаданные в файл."""
    
    with open(filepath, 'w', encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)

def load_table_data(table_name: str) -> list:
    """Загружает данные таблицы из файла."""

    filepath = Path(DATA_DIRECTORY) / f"{table_name}{TABLE_FILE_EXTENSION}"

    try:
        with open(filepath, 'r', encoding=ENCODING) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы в файл."""

    Path(DATA_DIRECTORY).mkdir(exist_ok=True)
    
    filepath = Path(DATA_DIRECTORY) / f"{table_name}{TABLE_FILE_EXTENSION}"
    
    with open(filepath, 'w', encoding=ENCODING) as f:
        json.dump(data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)