from flask import Flask, render_template, redirect, request, url_for
from utils import SQLite
import logging
import schedule
import time
import datetime
import threading
from pin_controller import (
    enable_all_lines,
    activate_line,
    deactivate_line,
    deactivate_all_lines,
)


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second


def load_schedules():
    with SQLite() as db:
        schedules = db.execute(
            """
            SELECT wl.gpio_pin, wl.name, ws.repeat_days, ws.start_time, ws.end_time
            FROM watering_schedule ws
            INNER JOIN watering_lines wl ON ws.watering_line_id = wl.id
        """
        ).fetchall()

    weakdays_dict = {
        "Mon": "monday",
        "Tue": "tuesday",
        "Wed": "wednesday",
        "Thu": "thursday",
        "Fri": "friday",
        "Sat": "saturday",
        "Sun": "sunday",
    }

    # Convert each schedule into jobs
    for schedule_item in schedules:
        gpio_pin = schedule_item["gpio_pin"]
        name = schedule_item["name"]
        days = schedule_item["repeat_days"].split(",")
        start_time = schedule_item["start_time"]
        end_time = schedule_item["end_time"]

        # Schedule the start and stop for each day
        for day_abrev, day_name in weakdays_dict.items():
            if day_abrev in days:
                getattr(schedule.every(), day_name).at(start_time).do(
                    start_watering, gpio_pin=gpio_pin, name=name
                )
                getattr(schedule.every(), day_name).at(end_time).do(
                    stop_watering, gpio_pin=gpio_pin, name=name
                )
    print(f"Loaded {len(schedules)} watering schedules.")


def start_watering(gpio_pin=-1, name="No Name"):
    if maintenance_check():
        print(
            f"Maintenance mode is active. Skipping watering starting for {name}, (PIN {
                gpio_pin})."
        )
        return
    activate_line(gpio_pin)
    print(f"{datetime.datetime.now()
             } - Watering started for {name}, (PIN {gpio_pin})")


def stop_watering(gpio_pin=-1, name="No Name"):
    if maintenance_check():
        print(
            f"Maintenance mode is active. Skipping watering endding for {name}, (PIN {
                gpio_pin})."
        )
        return
    deactivate_line(gpio_pin)
    print(f"{datetime.datetime.now()
             } - Watering stopped for {name}, (PIN {gpio_pin})")


def reload_schedules():
    schedule.clear()  # Clear existing jobs
    load_schedules()  # Reload from the database


def add_schedule(watering_line_id, start_time, end_time, repeat_days):
    with SQLite() as db:
        # Check for overlapping schedules
        # To overlap both must start before the other ends
        existing = db.execute(
            """
            SELECT *
            FROM watering_schedule
            WHERE start_time < ?
            AND end_time > ?
            """,
            (
                end_time,
                start_time,
            ),
        ).fetchall()

    used = {day for row in existing for day in row["repeat_days"].split()}

    if used.intersection(set(repeat_days.split())):
        raise ValueError("Schedule conflicts with an existing schedule.")

    with SQLite() as db:
        # Insert new schedule if no conflicts
        db.execute(
            """
        INSERT INTO watering_schedule (watering_line_id, start_time, end_time, repeat_days)
        VALUES (?, ?, ?, ?)
        """,
            (watering_line_id, start_time, end_time, repeat_days),
        )
    reload_schedules()  # Reload schedules to reflect the change


@app.route("/")
def home():
    """Home page with navigation links."""
    return render_template("home.html")


@app.route("/schedules/")
def list_schedules():
    """List all watering schedules."""
    with SQLite() as db:
        schedules = db.execute("""
        SELECT s.id, w.name AS watering_line, s.start_time, s.end_time, s.repeat_days
        FROM watering_schedule s
        JOIN watering_lines w ON s.watering_line_id = w.id
        ORDER By s.start_time
        """).fetchall()
    return render_template("list_schedules.html", schedules=schedules)


@app.route("/schedules/create", methods=["GET", "POST"])
def create_schedule():
    """Create a new watering schedule."""
    if request.method == "GET":
        with SQLite() as db:
            watering_lines = db.execute(
                "SELECT id, name FROM watering_lines"
            ).fetchall()
        return render_template("create_schedule.html", watering_lines=watering_lines)

    # POST: Handle form submission
    watering_line_id = int(request.form["watering_line_id"])
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]
    repeat_days = ",".join(request.form.getlist("repeat_days"))

    try:
        add_schedule(watering_line_id, start_time, end_time, repeat_days)
    except ValueError as e:
        return f"Error {e}", 400

    return redirect(url_for("list_schedules"))


@app.route("/schedules/edit/<int:schedule_id>", methods=["GET", "POST"])
def edit_schedule(schedule_id):
    """Edit an existing watering schedule."""
    with SQLite() as db:
        if request.method == "GET":
            schedule = db.execute(
                "SELECT * FROM watering_schedule WHERE id = ?", (schedule_id,)
            ).fetchone()
            watering_lines = db.execute(
                "SELECT id, name FROM watering_lines"
            ).fetchall()

            if not schedule:
                return "Schedule not found", 404

            return render_template(
                "edit_schedule.html", schedule=schedule, watering_lines=watering_lines
            )

        # POST: Handle form submission
        watering_line_id = int(request.form["watering_line_id"])
        start_time = request.form["start_time"]
        end_time = request.form["end_time"]
        repeat_days = ",".join(request.form.getlist("repeat_days"))

        # Check for overlapping schedules
        existing = db.execute(
            """
        SELECT *
        FROM watering_schedule
        WHERE id != ?
          AND watering_line_id = ?
          AND (start_time < ? AND end_time > ?)
          AND (
              repeat_days LIKE '%' || ? || '%'
          )
        """,
            (schedule_id, watering_line_id, end_time, start_time, repeat_days),
        ).fetchall()

        if existing:
            return "Schedule conflicts with an existing schedule.", 400

        # Update the schedule
        db.execute(
            """
        UPDATE watering_schedule
        SET watering_line_id = ?, start_time = ?, end_time = ?, repeat_days = ?
        WHERE id = ?
        """,
            (watering_line_id, start_time, end_time, repeat_days, schedule_id),
        )

    reload_schedules()  # Reload schedules to reflect the change
    return redirect(url_for("list_schedules"))


@app.route("/schedules/delete/<int:schedule_id>")
def delete_schedule(schedule_id):
    """Delete a watering schedule."""
    with SQLite() as db:
        db.execute("DELETE FROM watering_schedule WHERE id = ?", (schedule_id,))
    reload_schedules()  # Reload schedules to reflect the change
    return redirect(url_for("list_schedules"))


@app.route("/lines/")
def list_lines():
    with SQLite() as db:
        water_lines = db.execute("SELECT * FROM watering_lines").fetchall()
    return render_template("list_lines.html", watering_lines=water_lines)


@app.route("/lines/delete/<int:line_id>")
def delete_line(line_id):
    try:
        with SQLite() as db:
            db.execute("DELETE FROM watering_lines WHERE id = ?", (line_id,))
        logging.info(f"Deleted watering line with ID: {line_id}")
    except Exception as e:
        logging.error(f"Failed to delete watering line: {e}")
        return "An error occurred.", 500

    return redirect(url_for("list_lines"))


# Route to display the form and handle submission
@app.route("/lines/create", methods=["GET", "POST"])
def create_line():
    if request.method == "GET":
        return render_template("create_line.html")

    # Get data from the form
    name = request.form["name"].strip()
    try:
        gpio_pin = int(request.form["gpio_pin"])
    except ValueError:
        return "Invalid GPIO Pin. It must be an integer", 400

    if not name:
        return "Name is required", 400

    # Insert the new watering line into the database
    with SQLite() as db:
        existing_pin = db.execute(
            "SELECT id FROM watering_lines WHERE gpio_pin = ?", (gpio_pin,)
        ).fetchone()
        if existing_pin:
            return "GPIO Pin is already in use.", 400

        db.execute(
            "INSERT INTO watering_lines (name, gpio_pin) VALUES (?, ?)",
            (name, gpio_pin),
        )
    # Redirect to a page listing watering lines
    return redirect(url_for("list_lines"))


@app.post("/lines/edit/<int:line_id>")
def edit_line_post(line_id):
    # Get updated data from the form
    name = request.form["name"].strip()
    try:
        gpio_pin = int(request.form["gpio_pin"])
    except ValueError:
        return "Invalid GPIO Pin. It must be an integer", 400
    test = dict(request.form)
    test["line_id"] = line_id
    with SQLite() as db:
        # Update the watering line in the database
        db.execute(
            "UPDATE watering_lines SET name = ?, gpio_pin = ? WHERE id = ?",
            (name, gpio_pin, line_id),
        )

    # Redirect to the list page
    return redirect(url_for("list_lines"))


@app.get("/lines/edit/<int:line_id>")
def edit_line(line_id):
    with SQLite() as db:
        # For GET requests, fetch the current watering line details
        line = db.execute(
            "SELECT * FROM watering_lines WHERE id = ?", (line_id,)
        ).fetchone()

    if not line:
        # If no record is found, return a 404 error
        return "Watering line not found", 404

    # Pass the current details to the edit form
    return render_template("edit_line.html", line=line)


@app.route("/maintenance", methods=["GET", "POST"])
def maintenance():
    """Page to test and toggle watering lines."""
    with SQLite() as db:
        watering_lines = db.execute("SELECT * FROM watering_lines").fetchall()
        mode = db.execute(
            "SELECT value FROM settings WHERE key = 'maintenance_mode'"
        ).fetchone()["value"]
    if request.method == "POST":
        # Handle toggling
        line_id = int(request.form["line_id"])
        action = request.form["action"]

        # Get the GPIO pin for the selected watering line
        line = next(
            (line for line in watering_lines if line["id"] == line_id), None)

        if line:
            gpio_pin = line["gpio_pin"]

            if action == "on":
                activate_line(gpio_pin)  # Turn the line on
            elif action == "off":
                deactivate_line(gpio_pin)  # Turn the line off

    return render_template("maintenance.html", watering_lines=watering_lines, mode=mode)


@app.route("/maintenance/toggle_maintenance", methods=["POST"])
def toggle_maintenance():
    with SQLite() as db:
        mode = db.execute(
            "SELECT value FROM settings WHERE key = 'maintenance_mode'"
        ).fetchone()["value"]
        new_mode = "on" if mode == "off" else "off"
        db.execute(
            "UPDATE settings SET value = ? WHERE key = 'maintenance_mode'", (
                new_mode,)
        )
    deactivate_all_lines()
    return redirect(url_for("maintenance"))


def maintenance_check():
    with SQLite() as db:
        maintenance = db.execute(
            "SELECT value FROM settings WHERE key = 'maintenance_mode'"
        ).fetchone()["value"]
    return maintenance == "on"


if __name__ == "__main__":
    # initlise all pins as outputs in a inactive state.
    enable_all_lines()

    # Start the scheduler on a background thread
    load_schedules()
    threading.Thread(target=run_schedule, daemon=True).start()

    # start webserver
    app.run(debug=False, host="0.0.0.0")
