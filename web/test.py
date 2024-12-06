from flask import Flask, render_template, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired
import sqlite3


app = Flask(__name__)

# Path to your SQLite database file
DATABASE = "watering_system.db"


# Function to get a connection to the SQLite3 database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This makes results return as dictionaries
    return conn


class MyForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    choice = RadioField("choice", choices=[1, 2, 3])
    button = SubmitField("btn")


@app.route("/")
def home():
    schedule_data = [
        {"Name": "Grass", "Status": "Next at 7:30", "Schedule": "Mon 6am 1hr"},
        {"Name": "Ferns", "Status": "Watering", "Schedule": "Tues 5pm 1hr"},
        # add more data if needed
    ]

    return render_template("index.html", schedule_data=schedule_data)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    form = MyForm(meta={"csrf": False})
    if form.validate_on_submit():
        return redirect("/success")
    return render_template("submit.html", form=form)


# Route to display the form and handle submission
@app.route("/create_line", methods=["GET", "POST"])
def create_line():
    if request.method == "POST":
        # Get data from the form
        name = request.form["name"]
        gpio_pin = int(request.form["gpio_pin"])

        # Insert the new watering line into the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO watering_lines (name, gpio_pin) VALUES (?, ?)",
            (name, gpio_pin),
        )
        conn.commit()
        conn.close()

        # Redirect to a page listing watering lines
        return redirect(url_for("list_lines"))

    return render_template("create_line.html")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
