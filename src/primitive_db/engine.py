import shlex

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def print_help():
    """Выводит справочное сообщение."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 

def run():
    """Основной цикл программы."""

    print("\n***База данных***")
    print_help()
    
    while True:
        try:
            # Загрузка актуальных метаданных
            metadata = load_metadata()
            
            # Запрос команды
            user_input = input(">>>Введите команду: ").strip()
            
            # Выход из программы
            if user_input.lower() == "exit":
                print("Выход из программы.")
                break
            
            # Пропуск пустых строк
            if not user_input:
                continue
            
            # Разбор команды
            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"Некорректный ввод: {e}. Попробуйте снова.")
                continue
            
            command = args[0]
            
            # Обработка команд
            if command == "create_table":
                if len(args) < 3:
                    print("Некорректное использование команды create_table.")
                    print("Использование: create_table <имя_таблицы> <столбец1:тип> ...")
                    continue
                
                table_name = args[1]
                columns = args[2:]
                
                # Обновление метаданных
                metadata = create_table(metadata, table_name, columns)
                if table_name in metadata:  # Если создание успешно
                    save_metadata(metadata)
            
            elif command == "drop_table":
                if len(args) != 2:
                    print("Некорректное использование команды drop_table.")
                    print("Использование: drop_table <имя_таблицы>")
                    continue
                
                table_name = args[1]
                
                # Удаление таблицы и сохранение изменений
                old_len = len(metadata)
                metadata = drop_table(metadata, table_name)
                if len(metadata) < old_len:  # Если удаление успешно
                    save_metadata(metadata)
            
            elif command == "list_tables":
                list_tables(metadata)
            
            elif command == "help":
                print_help()
            
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}. Попробуйте снова.")
