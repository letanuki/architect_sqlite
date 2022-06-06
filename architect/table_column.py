# coding: utf-8
from enum import Enum
from typing import Optional

# from .db_table import DbTable


class ColumnType(Enum):
    """
    Associate a type with it's script name
    """
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    BLOB = "BLOB"
    REAL = "REAL"
    NULL = "NULL"


class TableColumn:
    """
    Column from a database table
    """

    def __init__(self, key, name, autoincrement, pk, column_type, not_null):

        self._key: str = key
        self._name: str = name
        self._autoincrement: bool = autoincrement
        self._pk: bool = pk
        self._type: int = column_type
        self._not_null: bool = not_null
        self._fk: bool = False
        self._fk_table = None
        self._fk_column: Optional[TableColumn] = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def fk(self):
        return self._fk

    @property
    def pk(self):
        return self._pk

    @property
    def fk_table(self):
        return self._fk_table

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def not_null(self):
        return self._not_null

    @property
    def fk_column(self):
        return self._fk_column

    def add_fk(self, table, column):
        """Set this column as a foreign key from another table.

        :param table: other table
        :type table: DbTable
        :param column: primary in other table
        :type column: TableColumn
        """

        self._fk = True
        self._fk_table = table
        self._fk_column = column

    def graph(self, lvl=8):
        """display object as a one liner with it's information"""
        s = ''
        if self._fk:
            s += f'FK {self._fk_table.name}.{self._fk_column._name}'

        return f"{' '*lvl}>{self._name}({self.key=}) {' PK' * self._pk} {s}"
