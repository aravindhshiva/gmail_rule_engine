import sys

import jsonschema
import click
import sqlite3

from loader.loader import Loader
from rule_engine.engine import Engine

from logutils.utils import get_logger

log = get_logger()

@click.command()
@click.option('--init', help='Initialize the database.', is_flag=True)
@click.option('--load', help='Load the database.', is_flag=True)
@click.option('--process', help='Process rules.', is_flag=True)
@click.option('--force-init',
              help='Force initialize the database. (deletes the database if it exists, and re-initializes it)',
              is_flag=True)
def cli(init, load, process, force_init):
    if not init and force_init:
        log.failure("--init must be passed to be able to force initialization.")
        sys.exit(1)

    if not init and not load and not process:
        log.failure("Any one operation mode of --load, --init or --process must be passed.")
        sys.exit(1)

    try:
        if init:
            from db.init_db import init_db
            init_db(force_init)
    except sqlite3.Error as e:
        log.failure("Cannot initialize database due to error: ", e)

    if load:
        loader = Loader()
        loader.load()

    try:
        if process:
            engine = Engine(rules_json_path="rule_engine/rules.json")
            engine.process()
    except sqlite3.OperationalError as e:
        log.failure("Cannot process rules, make sure the database is populated.")
        log.failure(e)
        sys.exit(1)
    except TypeError as e:
        if e == "Invalid condition type.":
            log.failure("Cannot process rules, invalid condition type passed.")
        else:
            log.failure("It is not allowed to remove and add same labels. "
                  "This can happen if you have both 'mark_as_read' and 'mark_as_unread' in rule configuration.")
        sys.exit(1)
    except jsonschema.exceptions.ValidationError as e:
        log.failure("Provided rules JSON is invalid. Please check your rules configuration.")
        log.failure(e)
        sys.exit(1)


if __name__ == '__main__':
    cli()
