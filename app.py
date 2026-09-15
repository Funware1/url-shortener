from flask import Flask, render_template, request, redirect, url_for
import string
import random
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("urls.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()



def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits

    short_code = ''.join(
        random.choice(characters)
        for _ in range(length)
    )

    return short_code

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        original_url = request.form["url"]

        short_code = generate_short_code()

        conn = sqlite3.connect("urls.db")

        conn.execute(
            "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
            (original_url, short_code)
        )

        conn.commit()
        conn.close()

        short_url = url_for(
            "redirect_to_url",
            short_code=short_code,
            _external=True
        )

        return render_template(
            "index.html",
            short_url=short_url
        )

    return render_template("index.html")


@app.route("/<short_code>")
def redirect_to_url(short_code):

    conn = sqlite3.connect("urls.db")

    result = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return "URL not found", 404


if __name__ == "__main__":
    init_db()
    app.run(debug=True)