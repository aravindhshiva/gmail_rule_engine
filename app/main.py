import sys

import jsonschema
import click
import sqlite3

from loader.loader import Loader
from rule_engine.engine import Engine

@click.command()
@click.option('--init', help='Initialize the database.', is_flag=True)
@click.option('--load', help='Load the database.', is_flag=True)
@click.option('--process', help='Process rules.', is_flag=True)
@click.option('--force-init',
              help='Force initialize the database. (deletes the database if it exists, and re-initializes it)',
              is_flag=True)
def cli(init, load, process, force_init):
    try:
        if init:
            from db.init_db import init_db
            init_db(force_init)
    except sqlite3.Error as e:
        print("Cannot initialize database due to error: ", e)

    if load:
        loader = Loader()
        loader.load()

    try:
        if process:
            engine = Engine(rules_json_path="rule_engine/rules1.json")
            engine.process()
    except sqlite3.OperationalError as e:
        print(e)
        print("Cannot process rules, make sure the database is populated.")
        sys.exit(1)
    except TypeError as e:
        print(e)
        print("It is not allowed to remove and add same labels. "
              "This can happen if you have both 'mark_as_read' and 'mark_as_unread' in rule configuration.")
        sys.exit(1)
    except jsonschema.exceptions.ValidationError as e:
        print("Provided rules JSON is invalid. Please check your rules configuration.")
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    cli()
