"""
Gmail Rule Engine CLI - Main entry point for the application.
Provides command-line interface for initializing, loading, and processing email rules.
"""
from pathlib import Path
from typing import NoReturn

import click
import jsonschema
import sqlite3

from db.init_db import init_db
from loader.loader import Loader
from logutils.utils import get_logger
from rule_engine.engine import Engine

log = get_logger()

RULES_PATH = Path("rule_engine/rules.json")


def handle_db_init(force=False):
    try:
        init_db(force)
    except sqlite3.Error as e:
        log.failure(f"Cannot initialize database: {e}")
        raise click.Abort()


def handle_email_load():
    try:
        loader = Loader()
        loader.load()
    except FileNotFoundError:
        log.failure("Cannot load database because it is not initialized.")
        raise click.Abort()


def invoke_rule_engine():
    try:
        engine = Engine(rules_json_path=str(RULES_PATH))
        engine.process()
    except sqlite3.OperationalError as e:
        log.failure(f"Cannot process rules, database error: {e}")
        raise click.Abort()
    except TypeError as e:
        if str(e) == "Invalid condition type.":
            log.failure("Cannot process rules, invalid condition type passed.")
        else:
            log.failure(
                "Conflicting label operations detected: Cannot both add and remove "
                "the same labels (e.g., mark_as_read and mark_as_unread)"
            )
        raise click.Abort()
    except jsonschema.exceptions.ValidationError as e:
        log.failure("Rules JSON is invalid:")
        log.failure(str(e))
        raise click.Abort()


@click.command()
@click.option('--init', help='Initialize the database.', is_flag=True)
@click.option('--load', help='Load the database.', is_flag=True)
@click.option('--process', help='Process rules.', is_flag=True)
@click.option(
    '--force-init',
    help='Force initialize the database (deletes existing database).',
    is_flag=True
)
def cli(init: bool, load: bool, process: bool, force_init: bool) -> NoReturn:
    """
    Gmail Rule Engine CLI Entrypoint.

    Initializes the database, loads emails and process rules against loaded emails.
    """
    if not init and force_init:
        log.failure("--init must be passed to use --force-init")
        raise click.Abort()

    if not any([init, load, process]):
        log.failure("One operation mode (--load, --init or --process) must be specified")
        raise click.Abort()

    if init:
        handle_db_init(force_init)

    if load:
        handle_email_load()

    if process:
        invoke_rule_engine()


if __name__ == '__main__':
    cli()