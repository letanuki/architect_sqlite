# coding: utf-8
from enum import Enum

from .abstract_builder import AbstractBuilder
from architect import DB, DbTable, TableColumn


class ColumnType(Enum):
    """
    Associate a type with it's script name
    """
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    BLOB = "BLOB"
    REAL = "REAL"
    NULL = "NULL"


class SQLiteScriptBuilder(AbstractBuilder):

    COMMENT = "--"

    @classmethod
    def dump(cls, db: DB) -> str:
        return f"{cls.generate_header()}\n{cls._dump_db(db)}"

    @classmethod
    def _dump_db(cls, db: DB) -> str:
        """Create sqlite script lines to create db database.

        :return: sqlite script line
        :rtype: str
        """
        tables = {k: cls._dump_table(v) for k, v in db.tables.items()}

        tables_to_dump = []
        table_dumped_key = []

        # while inserting table in script, we need to respect relations order.
        while 1:

            key_to_remove = []
            for k, v in tables.items():

                # current table can be inserted next only if tables with foreign key in current table are already
                # inserted
                to_insert = True
                for fk_table_key in db.tables[k].foreign_tables_key():
                    if fk_table_key not in table_dumped_key:
                        to_insert = not to_insert
                        break

                if not to_insert:
                    continue

                # adding table as next table to insert
                tables_to_dump.append(v)

                # next iterations and loops we will be able to insert table with a relation implying current table
                # primary key
                table_dumped_key.append(k)

                key_to_remove.append(k)

            # removing already inserted tables
            for k in key_to_remove:
                del tables[k]

            if len(tables) <= 0:
                break

        return "\n\n".join(tables_to_dump)

    @classmethod
    def _dump_table(cls, table: DbTable) -> str:
        """Create sqlite script lines to create table.

        :return: sqlite script line
        :rtype: str
        """
        lines_iterator = (cls._dump_column(v) for v in table.columns.values())
        columns_str = ",\n".join(lines_iterator)
        return f"CREATE TABLE {table.name} (\n{columns_str}\n);"

    @classmethod
    def _dump_column(cls, column: TableColumn) -> str:
        """Create sqlite script lines to create this column.

        managed: primary key, foreign key, not null

        :return: sqlite script line
        :rtype: str
        """

        type_assoc_map = {
            4: ColumnType.INTEGER,
            -2: ColumnType.BLOB,
            12: ColumnType.TEXT,
            1: ColumnType.TEXT,
        }

        str_type = type_assoc_map.get(column.type, ColumnType.INTEGER).value
        not_null_str = " NOT NULL" * column.not_null * (not column.pk)
        pk_str = " PRIMARY KEY" * column.pk
        fk_str = f"  REFERENCES {column.fk_table.name}({column.fk_column.name})"*column.fk if column.fk else ''

        line = f"{' ' * 16}{column.name} {str_type}{not_null_str}{pk_str}{fk_str}"
        return line
