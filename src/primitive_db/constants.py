# === ТИПЫ ДАННЫХ ===
TYPE_INT = "int"
TYPE_BOOL = "bool"
TYPE_STR = "str"
SUPPORTED_TYPES = {TYPE_INT, TYPE_STR, TYPE_BOOL}

# === ЗНАЧЕНИЯ BOOL ===
BOOL_TRUE_VALUES = ["true", "yes", "да"]
BOOL_FALSE_VALUES = ["false", "no", "нет"]

# === СТРУКТУРА ТАБЛИЦ ===
ID_COLUMN = "ID"
DEFAULT_ID_COLUMN = f"{ID_COLUMN}:{TYPE_INT}"

# === СИМВОЛЫ И РАЗДЕЛИТЕЛИ ===
COLUMN_TYPE_SEPARATOR = ":"
QUOTE_CHARS = {'"', "'"}
OPEN_PAREN = '('
CLOSE_PAREN = ')'
COMMA = ','
SPACE = ' '
EQUALS_SIGN = '='
QUOTE_SINGLE = "'"
QUOTE_DOUBLE = '"'

# === КОМАНДЫ И КЛЮЧЕВЫЕ СЛОВА ===

# Ключевые слова в командах
KEYWORD_INTO = "into"
KEYWORD_VALUES = "values"
KEYWORD_FROM = "from"
KEYWORD_WHERE = "where"
KEYWORD_SET = "set"

# === ПОЗИЦИИ АРГУМЕНТОВ ===
# Общие позиции
POS_COMMAND = 0
POS_FIRST_ARG = 1

# create_table: create_table <table_name> <column1:type> ...
POS_CREATE_TABLE_NAME = 1
POS_CREATE_COLUMNS_START = 2

# drop_table: drop_table <table_name>
POS_DROP_TABLE_NAME = 1

# insert: insert into <table_name> values (...)
POS_INSERT_KEYWORD_INTO = 1
POS_INSERT_TABLE_NAME = 2
POS_INSERT_KEYWORD_VALUES = 3
POS_INSERT_VALUES_START = 4

# select: select from <table_name> [where ...]
POS_SELECT_KEYWORD_FROM = 1
POS_SELECT_TABLE_NAME = 2
POS_SELECT_KEYWORD_WHERE = 3
POS_SELECT_WHERE_START = 4

# update: update <table_name> set ... where ...
POS_UPDATE_TABLE_NAME = 1
POS_UPDATE_KEYWORD_SET = 2
# WHERE позиция определяется динамически

# delete: delete from <table_name> where ...
POS_DELETE_KEYWORD_FROM = 1
POS_DELETE_TABLE_NAME = 2
POS_DELETE_KEYWORD_WHERE = 3
POS_DELETE_WHERE_START = 4

# info: info <table_name>
POS_INFO_TABLE_NAME = 1

# === МИНИМАЛЬНОЕ КОЛИЧЕСТВО АРГУМЕНТОВ ===
MIN_ARGS_CREATE_TABLE = 3  # create_table + имя + хотя бы 1 столбец
MIN_ARGS_DROP_TABLE = 2  # drop_table + имя
MIN_ARGS_INSERT = 5  # insert into <table> values (...)
MIN_ARGS_SELECT = 3  # select from <table>
MIN_ARGS_UPDATE = 7  # update <table> set ... where ...
MIN_ARGS_DELETE = 5  # delete from <table> where ...
MIN_ARGS_INFO = 2  # info <table>

# === ФАЙЛОВАЯ СИСТЕМА ===
DEFAULT_METADATA_FILE = "db_meta.json"
DATA_DIRECTORY = "data"
TABLE_FILE_EXTENSION = ".json"
ENCODING = "utf-8"
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

# === РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ ===
ASSIGNMENT_PATTERN = r'^\s*(\w+)\s*=\s*([^=]+?)\s*$'

# === КЭШИРОВАНИЕ ===
CACHE_KEY_FORMAT = "{where_clause}_{table_hash}"
