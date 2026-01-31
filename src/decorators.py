import json
import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок, связанных с операциями базы данных.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except IndexError:
            print("Ошибка: Таблица пуста или не содержит записей")
        except FileNotFoundError:
            print("Ошибка: Файл данных таблицы не найден")
        except json.JSONDecodeError:
            print("Ошибка: Файл данных поврежден (некорректный JSON)")
        except KeyError as e:
            print(f"Ошибка: Ключ не найден - {e}")
        except TypeError:
            print("Ошибка: Некорректный тип данных")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

def confirm_action(action_name):
    """
    Декоратор с аргументом, который запрашивает подтверждение пользователя
    перед выполнением опасной операции.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(
                f'\nВы уверены, что хотите выполнить "{action_name}"? [y/n]: ', 
                end=''
            )
            user_input = input().strip().lower()
            
            if user_input == 'y':
                return func(*args, **kwargs)
            else:
                print(f'Операция "{action_name}" отменена.')
                return args[0] if args else None
            
        return wrapper
    
    return decorator

def log_time(func):
    """
    Декоратор, который замеряет время выполнения функции и выводит его в консоль.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        
        execution_time = end_time - start_time
        print(f'Функция {func.__name__} выполнилась за {execution_time:.6f} сек.')
        
        return result
    
    return wrapper

def create_cacher():
    """Создает замыкание с кэшем и возвращает функцию для работы с ним."""

    cache = {}
    
    def cache_result(key, value_func):
        """
        Внутренняя функция, которая кэширует результаты.
        
        Args:
            key: Ключ для кэша (должен быть хэшируемым)
            value_func: Функция для получения данных, если их нет в кэше
            
        Returns:
            Результат из кэша или результат выполнения value_func
        """

        cache_key = str(key)
        
        if cache_key in cache:
            return cache[cache_key]
        
        result = value_func()
        cache[cache_key] = result
        return result
    
    return cache_result