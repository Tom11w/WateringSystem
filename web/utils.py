import sqlite3

# Path to your SQLite database file
DATABASE = "watering_system.db"


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


# Context manager to get a connection cursor to the SQLite3 database
class SQLite:
    def __init__(self, file=DATABASE):
        self.file = file

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(self.file)
            self.conn.row_factory = dict_factory
            return self.conn
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection failed: {e}")

    def __exit__(self, type, value, traceback):
        if self.conn:
            if traceback is None:  # Commit only if no exception occurred
                self.conn.commit()
            self.conn.close()
