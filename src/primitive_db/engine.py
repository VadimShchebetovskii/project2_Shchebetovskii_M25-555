import shlex

from prettytable import PrettyTable

from .constants import (
    KEYWORD_FROM,
    # Ключевые слова
    KEYWORD_INTO,
    KEYWORD_SET,
    KEYWORD_VALUES,
    KEYWORD_WHERE,
    # Минимальное количество аргументов
    MIN_ARGS_CREATE_TABLE,
    MIN_ARGS_DELETE,
    MIN_ARGS_DROP_TABLE,
    MIN_ARGS_INFO,
    MIN_ARGS_INSERT,
    MIN_ARGS_SELECT,
    MIN_ARGS_UPDATE,
    # Позиции аргументов
    POS_COMMAND,
    POS_CREATE_TABLE_NAME,
    POS_DELETE_KEYWORD_FROM,
    POS_DELETE_KEYWORD_WHERE,
    POS_DELETE_TABLE_NAME,
    POS_DELETE_WHERE_START,
    POS_DROP_TABLE_NAME,
    POS_FIRST_ARG,
    POS_INFO_TABLE_NAME,
    POS_INSERT_KEYWORD_INTO,
    POS_INSERT_KEYWORD_VALUES,
    POS_INSERT_TABLE_NAME,
    POS_SELECT_KEYWORD_FROM,
    POS_SELECT_KEYWORD_WHERE,
    POS_SELECT_TABLE_NAME,
    POS_SELECT_WHERE_START,
    POS_UPDATE_KEYWORD_SET,
    POS_UPDATE_TABLE_NAME,
)
from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_set_clause, parse_values, parse_where_clause
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def _print_help():
    """Выводит справочное сообщение."""
    
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> "
          "values (<значение1>, <значение2>, ...) - создать запись.")
    print("<command> select from <имя_таблицы> "
          "where <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
          "where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> "
          "where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")
    print()


def _print_table(table_data: list):
    """Выводит данные таблицы в формате PrettyTable."""

    if not table_data:
        print("Нет данных для отображения.")
        return
    
    headers = list(table_data[0].keys())
    table = PrettyTable(headers)
    
    for record in table_data:
        row = [record[header] for header in headers]
        table.add_row(row)
    
    print(table)


def _table_exists(metadata: dict, table_name: str) -> bool:
    """Проверяет существование таблицы."""

    return table_name in metadata


def _ensure_table_exists(metadata: dict, table_name: str) -> bool:
    """Проверяет существование таблицы с выводом ошибки."""

    if not _table_exists(metadata, table_name):
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    
    return True


def _handle_create_table(args: list, metadata: dict) -> dict:
    """Обрабатывает команду create_table."""

    if len(args) < MIN_ARGS_CREATE_TABLE:
        print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
        return metadata
    
    table_name = args[POS_CREATE_TABLE_NAME]
    columns = args[POS_FIRST_ARG + 1:]
    metadata = create_table(metadata, table_name, columns)
    
    if _table_exists(metadata, table_name):
        save_metadata(metadata)
    
    return metadata


def _handle_drop_table(args: list, metadata: dict) -> dict:
    """Обрабатывает команду drop_table."""

    if len(args) != MIN_ARGS_DROP_TABLE:
        print("Использование: drop_table <имя_таблицы>")
        return metadata
    
    table_name = args[POS_DROP_TABLE_NAME]
    old_len = len(metadata)
    metadata = drop_table(metadata, table_name)
    
    if len(metadata) < old_len:
        save_table_data(table_name, [])
        save_metadata(metadata)
    
    return metadata


def _handle_insert(args: list, metadata: dict) -> None:
    """Обрабатывает команду insert."""

    if (len(args) < MIN_ARGS_INSERT or
            args[POS_INSERT_KEYWORD_INTO].lower() != KEYWORD_INTO or
            args[POS_INSERT_KEYWORD_VALUES].lower() != KEYWORD_VALUES):
        usage = "Использование: insert into <имя_таблицы> "
        usage += "values (<значение1>, <значение2>, ...)"
        print(usage)
        return
    
    table_name = args[POS_INSERT_TABLE_NAME]
    
    if not _ensure_table_exists(metadata, table_name):
        return
    
    # Значения начинаются после "values"
    values_str = ' '.join(args[POS_INSERT_KEYWORD_VALUES + 1:])
    values = parse_values(values_str)
    
    if not values:
        usage = "Использование: insert into <имя_таблицы> "
        usage += "values (<значение1>, <значение2>, ...)"
        print(usage)
        return
    
    updated_data = insert(metadata, table_name, values)
    if updated_data:
        save_table_data(table_name, updated_data)


def _handle_select(args: list, metadata: dict) -> None:
    """Обрабатывает команду select."""

    if len(args) < MIN_ARGS_SELECT or \
            args[POS_SELECT_KEYWORD_FROM].lower() != KEYWORD_FROM:
        
        print("Использование: select from <имя_таблицы> [where <условие>]")
        return
    
    table_name = args[POS_SELECT_TABLE_NAME]
    if not _ensure_table_exists(metadata, table_name):
        return
    
    table_data = load_table_data(table_name)
    if not table_data:
        print(f'Таблица "{table_name}" пуста.')
        return
    
    # Проверяем наличие условия WHERE
    if len(args) > POS_SELECT_WHERE_START and \
            args[POS_SELECT_KEYWORD_WHERE].lower() == KEYWORD_WHERE:

        where_str = ' '.join(args[POS_SELECT_WHERE_START:])
        where_clause = parse_where_clause(where_str)
        
        if not where_clause:
            print("Использование: select from <имя_таблицы> [where <условие>]")
            return
        
        result_data = select(table_data, where_clause)
        if not result_data:
            return
    elif len(args) == MIN_ARGS_SELECT:
        result_data = select(table_data)
        if not result_data:
            print(f'Таблица "{table_name}" пуста.')
            return
    else:
        print("Использование: select from <имя_таблицы> [where <условие>]")
        return
    
    _print_table(result_data)


def _handle_update(args: list, metadata: dict) -> None:
    """Обрабатывает команду update."""

    if len(args) < MIN_ARGS_UPDATE or \
            args[POS_UPDATE_KEYWORD_SET].lower() != KEYWORD_SET \
            or KEYWORD_WHERE not in args:
        usage = "Использование: update <имя_таблицы> "
        usage += "set <столбец>=<значение> where <условие>"
        print(usage)
        return
    
    table_name = args[POS_UPDATE_TABLE_NAME]
    if not _ensure_table_exists(metadata, table_name):
        return
    
    try:
        set_idx = args.index("set")
        where_idx = args.index("where")
    except ValueError:
        print("Некорректный синтаксис команды update.")
        usage = "Использование: update <имя_таблицы> "
        usage += "set <столбец>=<значение> where <условие>"
        print(usage)
        return
    
    set_str = ' '.join(args[set_idx + 1:where_idx])
    where_str = ' '.join(args[where_idx + 1:])
    
    set_clause = parse_set_clause(set_str)
    if not set_clause:
        usage = "Использование: update <имя_таблицы> "
        usage += "set <столбец>=<значение> where <условие>"
        print(usage)
        return
    
    where_clause = parse_where_clause(where_str)
    if not where_clause:
        usage = "Использование: update <имя_таблицы> "
        usage += "set <столбец>=<значение> where <условие>"
        print(usage)
        return
    
    table_data = load_table_data(table_name)
    if not table_data:
        print(f'Таблица "{table_name}" пуста.')
        return
    
    updated_data = update(table_data, set_clause, where_clause)
    
    if updated_data != table_data:
        save_table_data(table_name, updated_data)
        updated_count = sum(1 for i in range(len(table_data))
                            if table_data[i] != updated_data[i])
        message = f'Записей в таблице "{table_name}" успешно обновлено: '
        message += f'{updated_count}.'
        print(message)


def _handle_delete(args: list, metadata: dict) -> None:
    """Обрабатывает команду delete."""

    if (len(args) < MIN_ARGS_DELETE or
            args[POS_DELETE_KEYWORD_FROM].lower() != KEYWORD_FROM or
            args[POS_DELETE_KEYWORD_WHERE].lower() != KEYWORD_WHERE):
        print("Использование: delete from <имя_таблицы> where <условие>")
        return
    
    table_name = args[POS_DELETE_TABLE_NAME]
    if not _ensure_table_exists(metadata, table_name):
        return
    
    where_str = ' '.join(args[POS_DELETE_WHERE_START:])
    where_clause = parse_where_clause(where_str)
    
    if not where_clause:
        print("Использование: delete from <имя_таблицы> where <условие>")
        return
    
    table_data = load_table_data(table_name)
    if not table_data:
        print(f'Таблица "{table_name}" пуста.')
        return
    
    original_count = len(table_data)
    updated_data = delete(table_data, where_clause)
    deleted_count = original_count - len(updated_data)
    
    if deleted_count > 0:
        save_table_data(table_name, updated_data)
        message = f'Записей из таблицы "{table_name}" успешно удалено: '
        message += f'{deleted_count}.'
        print(message)


def _handle_info(args: list, metadata: dict) -> None:
    """Обрабатывает команду info."""

    if len(args) != MIN_ARGS_INFO:
        print("Использование: info <имя_таблицы>")
        return
    
    table_name = args[POS_INFO_TABLE_NAME]
    if _table_exists(metadata, table_name):
        info(metadata, table_name)
    else:
        print(f'Ошибка: Таблица "{table_name}" не существует.')


def run():
    """Основной цикл программы."""
    
    _print_help()
    
    while True:
        try:
            metadata = load_metadata()
            user_input = input(">>>Введите команду: ").strip()
            
            if user_input.lower() == "exit":
                print("Выход из программы.")
                break
            
            if not user_input:
                continue
            
            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"Некорректный ввод: {e}. Попробуйте снова.")
                continue
            
            command = args[POS_COMMAND].lower()
            
            if command == "create_table":
                metadata = _handle_create_table(args, metadata)
            
            elif command == "drop_table":
                metadata = _handle_drop_table(args, metadata)
            
            elif command == "list_tables":
                list_tables(metadata)
            
            elif command == "insert":
                _handle_insert(args, metadata)
            
            elif command == "select":
                _handle_select(args, metadata)
            
            elif command == "update":
                _handle_update(args, metadata)
            
            elif command == "delete":
                _handle_delete(args, metadata)
            
            elif command == "info":
                _handle_info(args, metadata)
            
            elif command == "help":
                _print_help()
            
            else:
                print(f"Неизвестная команда: {command}")
                
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")