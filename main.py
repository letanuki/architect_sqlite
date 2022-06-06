# coding: utf-8
from argparse import ArgumentParser

from architect import DB
from data_io import load_from_architect_file
from builder import SQLiteScriptBuilder, PythonScriptBuilder


def sqlite_script(db: DB, filepath: str):
    with open(filepath, "w") as fp:
        fp.write(SQLiteScriptBuilder.dump(db))


def python_script(db: DB, filepath: str):
    with open(filepath, "w") as fp:
        fp.write(PythonScriptBuilder.dump(db))


def launch(script, sqlite, py):

    db = load_from_architect_file(script)
    sqlite_script(db, sqlite)
    python_script(db, py)


def cmd_line_interface():
    """
    command line interface function.
    """
    parser = ArgumentParser()

    #
    # public args --> all user
    #

    # mandatory positional args : file/folder location
    parser.add_argument("script", help="architect script path(*.xml)", type=str)

    sqlite_default = "script.sqlite"
    parser.add_argument("-s", "--sqlite", help=f"sqlite file path, default:{sqlite_default}",
                        default=sqlite_default, type=str)

    py_default = "architect.py"
    parser.add_argument("-p", "--py", help=f"python file path, default:{py_default}",
                        default=py_default, type=str)

    args = parser.parse_args()

    launch(**args.__dict__)


if __name__ == "__main__":
    cmd_line_interface()
