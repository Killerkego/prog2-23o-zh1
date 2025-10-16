import os
from flask import Flask, render_template, request, redirect
import db

app = Flask(__name__)

if not os.path.exists(db.DATABASE):
    with app.app_context():
        db.init_db()

@app.get("/")
def index():
    return render_template("books.html", books = db.list_books(), members = db.list_members())

@app.post("/books")
def add_book():
    author = request.form.get("author", "")
    title = request.form.get("title", "")
    year = request.form["year"]
    publisher = request.form.get("publisher", "")
    isbn = request.form.get("isbn", "")
    year_int = int(year)

    if isbn and title:
        db.add_book(author=author, title=title, year=year_int, publisher=publisher, isbn=isbn)

    return redirect("/")

@app.route("/members", methods= ["GET", "POST"])
def members_site():
    if request.method == "POST":
        neptun = request.form.get("neptun", "")
        name = request.form.get("name", "")
        db.add_member(neptun = neptun, name = name)
    return render_template("members.html", members = db.list_members())

@app.route("/checkout", methods = ["GET", "POST"])
def borrow_book():
    if request.method == "POST":
        isbn = request.form.get("isbn", "")
        neptun = request.form.get("neptun", "")
        action = request.form.get("action", "")
        if action == "borrow":
            db.checkout(isbn=isbn, neptun=neptun)
        elif action == "return":
            db.return_book(isbn=isbn)
        return redirect("/")
    return render_template("books.html", books = db.list_books(), members = db.list_members())

if __name__ == "__main__":
    app.run(debug= True)