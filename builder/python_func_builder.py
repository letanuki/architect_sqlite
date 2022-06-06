# coding: utf-8
from .abstract_builder import AbstractBuilder
from architect import DB, DbTable


class PythonScriptBuilder(AbstractBuilder):

    COMMENT = "#"

    @classmethod
    def dump(cls, db: DB) -> str:
        """Create python functions to dump one or more row in each database's table.

        :param db: Database object
        :type db: DB
        :return: functions for each table
        :rtype: str
        """
        return f"{cls.generate_header()}\n{cls._dump_db(db)}"

    @classmethod
    def _dump_db(cls, db: DB) -> str:
        """Create python functions to dump one or more row in each database's table.

        :param db: Database object
        :type db: DB
        :return: functions for each table
        :rtype: str
        """

        dump_class = '''# coding: utf-8
import sqlite3
import os
import logging
from typing import List

with open("./ressources/sqlite/sqlite.sql", 'r', encoding="utf-8") as fp:
    SQLITE_CREATION_SCRIPT = fp.read()


logger = logging.getLogger(__name__)


def args_logger_decorator(func):
    """Decorate a function to log it's arguments"""
    def wrapper(*args, **kwargs):
        logger.debug(f"{{}}({{}}, {{}})".format(func.__name__, args, kwargs))
        return func(*args, **kwargs)
    return wrapper


class SqLiteRequestBuilder:

    INSERT_OR_ = "INSERT OR {operation} INTO {table} ({columns}) values ({question_mark_placeholder})"

    @classmethod
    def set_insert_or_x_request(cls, table: str, columns: List[str], operation: str = "FAIL"):
        """Create an "INSERT OR SOMETHING" sqlite request

        :param table: table name
        :type table: str
        :param columns: columns name
        :type columns: List[str]
        :param operation: operation to do in case of insertion fail
        :type operation: str
        :return: request
        :rtype: str
        """
        number_of_column = len(columns)
        return cls.INSERT_OR_.format(operation=operation,
                                     table=table,
                                     columns=", ".join(columns),
                                     question_mark_placeholder=', '.join("?" * number_of_column))


class ArchitectSQliteConnector:

    def __init__(self, filepath: str, erase_if_exists: bool, create: bool = True, **kwargs):

        if filepath != ':memory:':
            if os.path.isfile(filepath) and erase_if_exists:
                os.remove(filepath)

        self.conn = sqlite3.connect(filepath, **kwargs)

        if create or erase_if_exists:
            self.conn.executescript(SQLITE_CREATION_SCRIPT)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        '''

        tables_to_dump = []
        for table in db.tables.values():
            tables_to_dump.append(cls._dump_table(table))
        tables_str = "\n".join(tables_to_dump)
        return f'{dump_class}{tables_str}\n'

    @classmethod
    def _dump_table(cls, table: DbTable) -> str:
        """Create python functions to dump one or more row in table.

        :return: functions for table
        :rtype: str
        """
        fcn_name = table.name.lower()
        cols_name_no_pk = tuple(col.name for col in table.columns.values() if not col.pk)

        # in cols name, we put primary key at start
        cols_name = list(cols_name_no_pk)
        pk = table.primary_key()
        if pk is not None:
            cols_name.insert(0, pk.name)
            execute_values = f'None, {", ".join(cols_name_no_pk)}'
        else:
            execute_values = f'{", ".join(cols_name_no_pk)}'

        fcn = f'''
    @args_logger_decorator
    def _dump_row_{fcn_name}(self, {", ".join(cols_name_no_pk)}):
        """Dump a row in table {table.name}"""
        req = SqLiteRequestBuilder.set_insert_or_x_request("{table.name}", {cols_name}, "FAIL")
        return self.conn.execute(req, ({execute_values})) 
    
    @args_logger_decorator   
    def _dump_rows_{fcn_name}(self, rows, or_x="FAIL"):
        """Dump rows in table {table.name}
    
        In this function, you need to insert primary key values as None. and respect the same order as in table

        :param rows: rows to add to table
        :type rows: Iterable
        :param or_x: action to perform if insert fail, available: "ROLLBACK", "ABORT", "FAIL", "IGNORE", and "REPLACE"
        :type or_x: str
        :return: Cursor
        :rtype: sqlite3.Cursor
        """
        req = SqLiteRequestBuilder.set_insert_or_x_request("{table.name}", {cols_name}, or_x)
        return self.conn.executemany(req, rows)'''

        return fcn
