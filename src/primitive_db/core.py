import json

from ..decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .constants import (
    BOOL_FALSE_VALUES,
    BOOL_TRUE_VALUES,
    CACHE_KEY_FORMAT,
    COLUMN_TYPE_SEPARATOR,
    DEFAULT_ID_COLUMN,
    ID_COLUMN,
    QUOTE_CHARS,
    SUPPORTED_TYPES,
    TYPE_BOOL,
    TYPE_INT,
    TYPE_STR,
)
from .utils import load_table_data

_select_cacher = create_cacher()


def _parse_value(value_str: str, expected_type: str):
    """Парсит строковое значение в нужный тип."""
    
    value_str = value_str.strip()
    
    if expected_type == TYPE_INT:
        return int(value_str)
    
    elif expected_type == TYPE_BOOL:
        if value_str.lower() in BOOL_TRUE_VALUES:
            return True
        elif value_str.lower() in BOOL_FALSE_VALUES:
            return False
        else:
            raise ValueError(f"Невозможно преобразовать '{value_str}' в bool")
    
    elif expected_type == TYPE_STR:
        if len(value_str) >= 2 and value_str[0] in QUOTE_CHARS \
        and value_str[-1] in QUOTE_CHARS:
            
            return value_str[1:-1]
        return value_str
    
    else:
        raise ValueError(f"Неизвестный тип: {expected_type}")


def _validate_clause(table_data: list, clause: dict) -> bool:
    """Проверяет, что столбец в условии существует в таблице."""
    
    if not table_data:
        print("Ошибка: Таблица пуста.")
        return False
    
    first_record = table_data[0]
    clause_column = next(iter(clause))
    
    if clause_column not in first_record:
        valid_columns = ", ".join(sorted(first_record.keys()))
        print(f'Ошибка: Столбец "{clause_column}" не существует в таблице. '
              f'Допустимые столбцы: {valid_columns}')
        return False
    
    return True


def _matches_condition(record: dict, condition: dict) -> bool:
    """Проверяет, удовлетворяет ли запись условию."""

    for col, value in condition.items():
        if str(record.get(col, "")) != str(value):
            return False
        
    return True


def _get_next_id(table_data: list) -> int:
    """Возвращает следующий доступный ID для таблицы."""
    
    if not table_data:
        return 1
    return max(record.get(ID_COLUMN, 0) for record in table_data) + 1


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """Создает новую таблицу в метаданных."""
    
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    has_user_id = False
    table_columns = []
    
    for col_def in columns:
        if COLUMN_TYPE_SEPARATOR not in col_def:
            print(f"Некорректное значение: '{col_def}'. Попробуйте снова.")
            return metadata
        
        col_name, col_type = col_def.split(COLUMN_TYPE_SEPARATOR, 1)
        col_type = col_type.lower()
        
        if col_name.upper() == ID_COLUMN:
            has_user_id = True
        
        if col_type not in SUPPORTED_TYPES:
            print(f"Некорректное значение: '{col_def}'. Попробуйте снова.")
            return metadata
        
        table_columns.append(f"{col_name}:{col_type}")
    
    if not has_user_id:
        table_columns.insert(0, DEFAULT_ID_COLUMN)
    
    metadata[table_name] = table_columns
    print(f'Таблица "{table_name}" успешно создана со столбцами: '
          f'{", ".join(table_columns)}')
    
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    
    return metadata


def list_tables(metadata: dict) -> None:
    """Выводит список всех таблиц."""
    
    if not metadata:
        print("Нет созданных таблиц.")
        return
    
    for table_name in metadata:
        print(f"- {table_name}")


@log_time
@handle_db_errors
def insert(metadata: dict, table_name: str, values: list) -> list:
    """Добавляет новую запись в таблицу и возвращает обновленные данные."""
    
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []
    
    table_columns = metadata[table_name]
    user_columns_count = len(table_columns) - 1
    
    if len(values) != user_columns_count:
        print(f"Ошибка: Ожидается {user_columns_count} значений, "
              f"получено {len(values)}.")
        return []
    
    table_data = load_table_data(table_name)
    new_id = _get_next_id(table_data)
    new_record = {ID_COLUMN: new_id}

    for i, col_def in enumerate(table_columns[1:], 0):
        col_name, col_type = col_def.split(COLUMN_TYPE_SEPARATOR, 1)
        
        parsed_value = _parse_value(values[i], col_type)
        new_record[col_name] = parsed_value
    
    table_data.append(new_record)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    
    return table_data


@log_time
@handle_db_errors
def select(table_data: list, where_clause: dict = None) -> list:
    """Фильтрует записи из таблицы."""
    
    if not where_clause:
        return table_data

    table_hash = hash(json.dumps(table_data, sort_keys=True)) if table_data else 0
    cache_key = CACHE_KEY_FORMAT.format(
        where_clause=str(where_clause),
        table_hash=table_hash
    )
    
    def get_filtered_data():
        if not _validate_clause(table_data, where_clause):
            return []
        filtered_data = []
        for record in table_data:
            if _matches_condition(record, where_clause):
                filtered_data.append(record)
        return filtered_data
    
    return _select_cacher(cache_key, get_filtered_data)


@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет записи в данных таблицы."""

    if not _validate_clause(table_data, set_clause):
        return table_data
    if not _validate_clause(table_data, where_clause):
        return table_data

    updated_data = []
    
    for record in table_data:
        record_copy = record.copy()
        if _matches_condition(record_copy, where_clause):
            for col, new_value in set_clause.items():
                record_copy[col] = new_value
        
        updated_data.append(record_copy)
    
    return updated_data


@handle_db_errors
@confirm_action("удаление записей из таблицы") 
def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи из данных таблицы."""
    
    if not _validate_clause(table_data, where_clause):
        return table_data

    updated_data = []
    
    for record in table_data:
        record_copy = record.copy()
        if not _matches_condition(record_copy, where_clause):
            updated_data.append(record_copy)
    
    return updated_data


@handle_db_errors
def info(metadata: dict, table_name: str) -> None:
    """Выводит информацию о таблице."""
    
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return
    
    table_data = load_table_data(table_name)
    
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {', '.join(metadata[table_name])}")
    print(f"Количество записей: {len(table_data)}")