import sqlite3

# Path to your SQLite database file
DATABASE = "watering_system.db"


def create_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create the watering_lines table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watering_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gpio_pin INTEGER NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watering_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        watering_line_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        repeat_days TEXT NOT NULL,
        FOREIGN KEY (watering_line_id) REFERENCES watering_lines (id) ON DELETE CASCADE
    )
    """)

#   id:
#       A unique identifier for each schedule.

#   watering_line_id:
#       A foreign key referencing the id of the watering_lines table.
#       Ensures each schedule is associated with an existing watering line.

#   start_time and end_time:
#       Store the watering period in a 24-hour format
#       (e.g., "14:30" for 2:30 PM). Text format is sufficient since
#       comparisons between times as strings (in "HH:MM" format) are
#       lexicographically correct.

#   repeat_days:
#       Stores days of the week the schedule repeats, as a comma-separated
#       string (e.g., "Mon,Wed,Fri").

#   FOREIGN KEY Constraint:
#       Ensures that the watering_line_id corresponds to a valid record in the
#       watering_lines table. Includes ON DELETE CASCADE to automatically
#       remove schedules if the corresponding watering line is deleted.

    conn.commit()
    conn.close()


# Call the function to create the database and table
create_db()
