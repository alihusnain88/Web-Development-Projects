
from flask import Flask, render_template, request, redirect, session
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = "secret"

conn = pymysql.connect(
    host="your_host_name",
    user="your_user_name",
    password="your_database_password",  
    database="your_database_name",
    cursorclass=pymysql.cursors.DictCursor
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return redirect("/login")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)", (session["user_id"], title, content))
        conn.commit()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM notes WHERE user_id = %s", (session["user_id"],))
        notes = cursor.fetchall()
    return render_template("dashboard.html", notes=notes)

@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit(note_id):
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        with conn.cursor() as cursor:
            cursor.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s AND user_id=%s", (title, content, note_id, session["user_id"]))
        conn.commit()
        return redirect("/dashboard")
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM notes WHERE id=%s AND user_id=%s", (note_id, session["user_id"]))
        note = cursor.fetchone()
    return render_template("edit.html", note=note)

@app.route("/delete/<int:note_id>")
def delete(note_id):
    if "user_id" in session:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id=%s AND user_id=%s", (note_id, session["user_id"]))
        conn.commit()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
