import json


def load_metadata(filepath: str = "db_meta.json") -> dict:
    """Загружает метаданные из JSON-файла."""

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(data: dict, filepath: str = "db_meta.json") -> None:
    """Сохраняет метаданные в JSON-файл."""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)