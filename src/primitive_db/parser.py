import re

from .constants import (
    ASSIGNMENT_PATTERN,
    BOOL_FALSE_VALUES,
    BOOL_TRUE_VALUES,
    CLOSE_PAREN,
    COMMA,
    OPEN_PAREN,
    QUOTE_DOUBLE,
    QUOTE_SINGLE,
    SPACE,
)


def strip_quotes(value: str) -> str:
    """Убирает кавычки со строкового значения."""
    
    value = value.strip()
    if (value.startswith(QUOTE_DOUBLE) and value.endswith(QUOTE_DOUBLE)) or \
       (value.startswith(QUOTE_SINGLE) and value.endswith(QUOTE_SINGLE)):
        return value[1:-1]
    
    return value

def parse_assignment(assignment: str) -> tuple:
    """Парсит одно присваивание вида 'column = value'."""
    
    match = re.match(ASSIGNMENT_PATTERN, assignment, re.IGNORECASE)
    
    if not match:
        raise ValueError(f'Некорректное присваивание: "{assignment}". '
                         f'Ожидается формат: столбец = значение')
    
    column = match.group(1)
    value = match.group(2).strip()
    
    if value.lower() in BOOL_TRUE_VALUES:
        value = True
    elif value.lower() in BOOL_FALSE_VALUES:
        value = False
    else: 
        value = strip_quotes(value)

    return column, value

def parse_where_clause(where_str: str) -> dict:
    """Парсит условие WHERE."""
    
    if not where_str:
        return {}
    
    try:
        column, value = parse_assignment(where_str)
        return {column: value}
    except ValueError as e:
        print(f'Ошибка в условии WHERE: {e}')
        return None

def parse_set_clause(set_str: str) -> dict:
    """Парсит условие SET."""
    
    if not set_str:
        return {}
    
    result = {}
    
    try:
        column, value = parse_assignment(set_str)
        result[column] = value
    except ValueError as e:
        print(f'Ошибка в условии SET: {e}')
        return None
    
    return result

def parse_values(values_str: str) -> list:
    """Парсит строку значений для INSERT."""
    
    if not (values_str.startswith(OPEN_PAREN) and values_str.endswith(CLOSE_PAREN)):
        print("Ошибка: Значения должны быть заключены в скобки.")
        return None
    
    content = values_str[1:-1].strip()
    
    if not content:
        return []
    
    try:
        # Используем кастомный парсинг
        values = []
        i = 0
        n = len(content)
        
        while i < n:
            # Пропускаем пробелы
            while i < n and content[i] == SPACE:
                i += 1
            
            if i >= n:
                break
            
            # Обработка значения
            if content[i] in [QUOTE_DOUBLE, QUOTE_SINGLE]:
                # Строковое значение в кавычках
                quote_char = content[i]
                i += 1
                start = i
                
                # Ищем закрывающую кавычку
                while i < n and content[i] != quote_char:
                    i += 1
                
                if i >= n:
                    print("Ошибка: Незакрытые кавычки.")
                    return None
                
                value = content[start:i]
                i += 1  # Пропускаем закрывающую кавычку
            else:
                # Значение без кавычек (число, true, false)
                start = i
                while i < n and content[i] != COMMA:
                    i += 1
                
                value = content[start:i].strip()
            
            values.append(value)
            
            # Пропускаем запятую и пробелы
            while i < n and content[i] != COMMA:
                i += 1
            
            if i < n and content[i] == COMMA:
                i += 1  # Пропускаем запятую
        
        return values
        
    except Exception as e:
        print(f'Ошибка парсинга значений: {e}')
        return None