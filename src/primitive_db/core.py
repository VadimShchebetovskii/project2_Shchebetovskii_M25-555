def create_table(metadata: dict, table_name: str, columns: list) -> dict:
    """Создает новую таблицу в метаданных."""
    
    # Проверка существования таблицы
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    # Поддерживаемые типы данных
    supported_types = {"int", "str", "bool"}
    
    # Проверка, задал ли пользователь столбец ID
    has_user_id = False
    table_columns = []
    
    # Проверка и добавление столбцов
    for col_def in columns:
        if ':' not in col_def:
            print(f'Некорректное значение: {col_def}. Попробуйте снова.')
            return metadata
        
        col_name, col_type = col_def.split(':', 1)
        col_type = col_type.lower()
        
        # Проверяем, не ID ли это
        if col_name.upper() == "ID":
            has_user_id = True
        
        if col_type not in supported_types:
            print(f'Некорректное значение: {col_def}. Попробуйте снова.')
            return metadata
        
        table_columns.append(f"{col_name}:{col_type}")
    
    # Если пользователь не задал ID, добавляем его автоматически в начало
    if not has_user_id:
        table_columns.insert(0, "ID:int")
    
    # Сохраняем структуру таблицы в метаданные
    metadata[table_name] = table_columns

    print(f'Таблица "{table_name}" успешно создана со столбцами: {", ".join(table_columns)}')
    
    return metadata

def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных."""
    
    # Проверка существования таблицы
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    
    # Удаление таблицы
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
