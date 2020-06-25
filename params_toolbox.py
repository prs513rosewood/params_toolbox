"""
This module manages an sqlite database 'parameters.db' which contains
kinds of tables:
  - parameters tables
  - output tables
The functions defined here allow queries to the database.
"""

import os
import sqlite3
import atexit
import functools
import glob

connection = sqlite3.connect('parameters.db')
connection.row_factory = sqlite3.Row
cursor = connection.cursor()


def _check_identifier(_func=None, *, kind=""):
    "Check that identifiers are valid SQL column names"
    accepted_tables = {
        row['name'].split('_')[0]
        for row in connection.execute(
                'SELECT name FROM sqlite_master WHERE type="table"'
        )
    }

    accepted_kinds = {'parameters', 'output'}

    if _func is not None:
        table_kinds = accepted_kinds
    elif kind in accepted_kinds:
        table_kinds = [kind]
    else:
        raise ValueError('Table kind {} is invalid (accepted kinds {})'
                         .format(kind, accepted_kinds))

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            identifiers = list(kwargs.keys())
            if args[0] not in accepted_tables:
                raise ValueError(
                    ('Specified table {} does not exits '
                     '(accepted tables {})').format(args[0],
                                                    accepted_tables))

            accepted_keys = {'rowid'}

            for table in [args[0] + '_' + k for k in table_kinds]:
                columns = cursor.execute(f'PRAGMA table_info({table})') \
                                .fetchall()
                accepted_keys |= {col['name'] for col in columns}

            if not all(map(lambda x: x in accepted_keys, identifiers)):
                raise ValueError(
                    'Selection identifiers '
                    + '{} not all in accepted keys {}'.format(identifiers,
                                                              accepted_keys))

            return func(*args, **kwargs)
        return wrapper

    if _func is not None:
        return decorator(_func)
    else:
        return decorator


def _where(**kwargs):
    "Construct a WHERE statement from kwargs"
    table = kwargs.get('table')
    if table:
        request = f'{table}.{{k}}=?'
        kwargs.pop('table')
    else:
        request = '{k}=?'

    conditions = map(lambda k: request.format(k=k), kwargs.keys())
    try:
        return "WHERE " + functools.reduce(lambda a, b: a + " AND " + b,
                                           conditions)
    except TypeError:
        return ""


def execute(schema_file):
    "Execute a file containing SQL commands. Useful for database setup."
    with open(schema_file, 'r') as fh:
        statements = fh.read().replace('\n', ' ').split('; ')
        for statement in filter(lambda x: x != "", statements):
            cursor.execute(statement)
        connection.commit()


@_check_identifier(kind='parameters')
def get_param(table, **kwargs):
    """Return parameters for a given identifier in specified table"""
    request = f'SELECT rowid, * FROM {table}_parameters ' + _where(**kwargs)
    cursor.execute(request, tuple(kwargs.values()))
    results = cursor.fetchall()

    if len(results) == 1:
        return results[0]
    else:
        return results


@_check_identifier
def get_output(table, **kwargs):
    "Return parameters for a given identifier in specified table"
    request = (
        f'SELECT {table}_output.rowid, * FROM {table}_output '
        f'INNER JOIN {table}_parameters ON '
        f'{table}_output.{table}_id={table}_parameters.rowid '
        + _where(table=f'{table}_output', **kwargs)
    )
    cursor.execute(request, tuple(kwargs.values()))
    return cursor.fetchall()


@_check_identifier(kind='output')
def clean_output(table, **kwargs):
    "Remove output files registered in output table"
    request = f'DELETE FROM {table}_output ' + _where(**kwargs)
    choice = input(f'About to execute "{request}" with {kwargs}\n'
                   + 'Are you sure you want to delete '
                   + 'with output files (y or n)? ')
    if choice not in "y Yes yes".split():
        print("Not deleting")
        return

    def remove(f):
        print(f"Removing file {f}")
        os.remove(f)

    for row in get_output(table, **kwargs):
        files = glob.glob(row['file'] + '.*')
        for f in filter(os.path.isfile, files):
            remove(f)

    print("Deleting table record")
    cursor.execute(request, tuple(kwargs.values()))
    connection.commit()


@atexit.register
def _close_connection():
    print("[SQL] Closing connection")
    connection.close()
