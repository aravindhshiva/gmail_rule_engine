import sqlite3
import os

from logutils.utils import get_logger

log = get_logger()

def init_db(force=False):
    try:
        if os.path.exists(os.path.join("config", "email.db")) and not force:
            log.warning("⚠️  Database already exists, skipping initialization.")
            return

        if force and os.path.exists(os.path.join("config", "email.db")):
            log.warning("⚠️  Removing old database file due to force-init.")
            os.remove(os.path.join("config", "email.db"))

        log.success("Initializing database...")
        con = sqlite3.connect("config/email.db")
        cur = con.cursor()

        with open("config/init.sql", "r") as init_script:
            cur.executescript(init_script.read())

        con.commit()
        con.close()
    except sqlite3.Error as e:
        log.failure(e)


if __name__ == '__main__':
    init_db()