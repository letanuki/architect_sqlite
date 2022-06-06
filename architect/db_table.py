# coding: utf-8
from typing import Dict, Tuple

from .table_column import TableColumn


class DbTable:
    """
    Table from a database.
    """

    def __init__(self, key, name="", columns=None):

        self._key: str = key
        self._name: str = name
        self._columns: Dict[str, TableColumn] = {} if columns is None else columns

    @property
    def columns(self):
        return self._columns

    @property
    def name(self):
        return self._name

    @property
    def key(self):
        return self._key

    def graph(self, lvl=4):
        """display object with it's information and it's column."""
        s = f"{' '*lvl}-{self._name}({self.key=})\n"
        s += "\n".join((c.graph() for c in self._columns.values()))
        return s

    def foreign_tables_key(self):
        """
        :return: foreign keys key attribute in this table
        :rtype: Iterator[str, ...]
        """
        iterator = filter(lambda col: col.fk, self._columns.values())
        return (col.fk_table.key for col in iterator)

    def primary_key(self):
        t = tuple(filter(lambda col: col.pk, self._columns.values()))
        return t[0] if len(t)>0 else None
