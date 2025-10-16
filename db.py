import sqlite3
from flask import g

DATABASE = "library.sqlite"


def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        isbn TEXT UNIQUE,
        author TEXT,
        title TEXT,
        year INTEGER,
        publisher TEXT,
        borrowed BOOLEAN DEFAULT 0,
        borrowed_by TEXT DEFAULT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS members(
        neptun TEXT UNIQUE,
        name TEXT
    );
    """)
    db.commit()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory=sqlite3.Row
    return g.db

def list_books():
    db = get_db()
    cur = db.execute("SELECT * FROM books")
    rows = cur.fetchall()
    return rows

def list_members():
    db = get_db()
    cur = db.execute("SELECT * FROM members")
    rows = cur.fetchall()
    return rows

def add_member(neptun: str, name:str):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO members (neptun, name) VALUES (?, ?)",
        (neptun, name)
    )
    db.commit()
    return cur.lastrowid


def add_book(author: str, title: str, year: int, publisher: str, isbn: str):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO books (isbn, author, title, year, publisher) VALUES (?, ?, ?, ?, ?)",
        (isbn, author, title, year, publisher),
    )
    db.commit()
    return cur.lastrowid

def checkout(isbn: str, neptun: str) -> bool:
    """Attempt to borrow the book with given ISBN for member `neptun`.
    Returns True if successful, False if the book doesn't exist or is already borrowed.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT borrowed FROM books WHERE isbn = ?", (isbn,))
    row = cur.fetchone()
    if row is None:
        return False
    if row["borrowed"]:
        return False
    cur.execute(
        "UPDATE books SET borrowed = 1, borrowed_by = ? WHERE isbn = ?",
        (neptun, isbn),
    )
    db.commit()
    return True


def return_book(isbn: str) -> bool:
    """Return a borrowed book. Returns True if the book existed and was updated, False otherwise."""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT borrowed FROM books WHERE isbn = ?", (isbn,))
    row = cur.fetchone()
    if row is None:
        return False
    if not row["borrowed"]:
        return False
    cur.execute(
        "UPDATE books SET borrowed = 0, borrowed_by = NULL WHERE isbn = ?",
        (isbn,)
    )
    db.commit()
    return True

def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()