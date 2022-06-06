# coding: utf-8
from typing import Dict, Optional

from .db_table import DbTable


class DB:
    """
    Database object containing db tables in a dictionary.
    """

    def __init__(self, tables: Optional[Dict[str, DbTable]] = None):
        self._tables: Dict[str, DbTable] = {} if tables is None else tables

    @property
    def tables(self) -> Dict[str, DbTable]:
        return self._tables

    def graph(self):
        """display object with it's information and it's table."""
        s = 'table:\n'
        s += '\n'.join((table.graph() for table in self._tables.values()))
        return s

    def add_relation(self, pk_table_key, fk_table_key, pk_column_key, fk_column_key):
        """Add a relation between two columns

        :param pk_table_key:
        :type pk_table_key:
        :param fk_table_key:
        :type fk_table_key:
        :param pk_column_key:
        :type pk_column_key:
        :param fk_column_key:
        :type fk_column_key:
        """
        pk_table = self._tables[pk_table_key]
        pk_column = pk_table.columns[pk_column_key]

        fk_table = self._tables[fk_table_key]
        fk_column = fk_table.columns[fk_column_key]

        fk_column.add_fk(pk_table, pk_column)
