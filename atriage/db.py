import click

import shutil

import os

import sqlite3

import itertools


def create_tables(conn):
    conn.execute("""CREATE TABLE crashes (
                      crash_id INTEGER PRIMARY KEY,
                      path TEXT UNIQUE,
                      bucket INTEGER,
                      triage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )""")

    conn.execute("""CREATE TABLE metadata (
                      id INTEGER PRIMARY KEY CHECK (id = 0),
                      command TEXT,
                      current_bucket INTEGER,
                      db_version TEXT,
                      collector TEXT
                    )""")

    conn.execute("""CREATE TABLE exploitable (
                      crash_id INTEGER UNIQUE,
                      signal_info TEXT,
                      disassembly TEXT,
                      stack_trace TEXT,
                      faulting_frame TEXT,
                      description TEXT,
                      short_description TEXT,
                      hash_value TEXT,
                      exploitability TEXT,
                      explanation TEXT,
                      register_info TEXT,
                      FOREIGN KEY(crash_id) REFERENCES crashes(crash_id)
                    )""")

    conn.execute("""CREATE TABLE asan (
                      crash_id INTEGER UNIQUE,
                      asan_output TEXT,
                      FOREIGN KEY(crash_id) REFERENCES crashes(crash_id)
                    )""")

    conn.execute(
        """INSERT INTO metadata (id, command, current_bucket, db_version)
             VALUES (0, ?, -1, ?)""",
        (None, "0.2", )
    )

    conn.commit()


class AtriageDB(object):
    def __init__(self, db_file):
        self._db_file = db_file
        self._conn = self._init_conn(db_file)

    @property
    def command(self):
        c = self._conn.execute("SELECT command FROM metadata")
        return c.fetchone()[0]

    @command.setter
    def command(self, value):
        self._conn.execute("UPDATE metadata SET command=?", (value, ))
        self._conn.commit()

    @property
    def all_crashes(self):
        c = self._conn.execute("SELECT crash_id, path FROM crashes")
        return set([(i[0], self._make_relative_path(i[1]))
                    for i in c.fetchall()])

    @property
    def new_crashes(self):
        c = self._conn.execute("""SELECT crash_id, path FROM crashes
                                    WHERE bucket = (
                                      SELECT current_bucket FROM metadata
                                    )""")
        return set([(i[0], self._make_relative_path(i[1]))
                    for i in c.fetchall()])

    @property
    def raw_crashes(self):
        c = self._conn.execute(
            "SELECT path, bucket FROM crashes ORDER BY bucket ASC")
        groups = itertools.groupby(c.fetchall(), lambda x: x[1])
        return [set([self._make_relative_path(item[0]) for item in data])
                for (key, data) in groups]

    def get_result_set(self, index):
        """ Get crashes by index.

        Passing -1 as the index returns the latest set of crashes.
        """
        invalid_err = IndexError("Index {} is invalid. Use atriage info to "
                                 "view available indexes.".format(index))

        if index == -1:
            return self.new_crashes
        elif index < 0:
            raise invalid_err

        c = self._conn.execute("SELECT current_bucket FROM metadata")
        current_bucket = c.fetchone()[0]

        if index > current_bucket:
            raise invalid_err

        c = self._conn.execute("""SELECT crash_id, path FROM crashes
                                    WHERE bucket=?""", (index, ))
        return [(i[0], self._make_relative_path(i[1])) for i in c.fetchall()]

    def get_collector(self):
        """Get the collector used for the specific atriage database.
        """
        c = self._conn.execute("SELECT collector FROM metadata")
        return c.fetchone()[0]

    def set_collector(self, collector):
        """Set the collector used for the specific atriage database.
        """
        self._conn.execute("UPDATE metadata set collector=?",
                           (collector, ))

    def save_crashes(self, crashes):
        c = self._conn.execute("SELECT current_bucket FROM metadata")
        current_bucket = c.fetchone()[0]
        new_bucket = current_bucket + 1

        params = [(str(i), new_bucket) for i in crashes]
        self._conn.executemany("""INSERT OR IGNORE INTO crashes (path, bucket)
                                    VALUES (?, ?)""", params)

        c = self._conn.execute("UPDATE metadata SET current_bucket=?",
                               (new_bucket, ))

        self._conn.commit()

    def _init_conn(self, db):
        new_db = not os.path.isfile(db)

        _conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
        _conn.execute("PRAGMA foreign_keys = 1")

        if new_db:
            create_tables(_conn)

        return _conn

    def _make_relative_path(self, path):
        """Returns `path` relative to `self._db_file`."""
        return os.path.join(os.path.dirname(self._db_file), path)


def get_crash_statistics(db):
    """ Get crash statistics in a printable format.

    This function returns a tuple. The first value in the tuple is a formatted
    list of strings that is shows the new crashes added every time atriage is
    ran. The second value in the tuple is the total number of crashes.
    """
    out = []
    total_crashes = 0

    for index, value in enumerate(db.raw_crashes):
        num_crashes = len(value)
        total_crashes += num_crashes
        if index == 0:
            out.append((index, "{}".format(num_crashes)))
        else:
            out.append((index, "+{}".format(num_crashes)))

    return out, total_crashes


def copy_crashes(crashes, out):
    try:
        os.makedirs(out)
    except OSError as e:
        pass

    click.echo("Copying {} files...".format(len(crashes)))
    for i in crashes:
        try:
            shutil.copy2(str(i), out)
        except FileNotFoundError:
            click.echo("Error copying {}.".format(i))
