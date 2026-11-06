
import sqlite3
from flask import Blueprint, jsonify, request

from helpers import check
from database import get_connection

books_bp = Blueprint("books", __name__)


@books_bp.route("/books", methods=["GET"])
def list_books():
    conn = get_connection()

    if request.args.get("available") == "true":
        rows = conn.execute(
            "SELECT * FROM books WHERE available = 1"
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM books").fetchall()

    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "title": r[1],
            "author": r[2],
            "isbn": r[3],
            "available": bool(r[4])
        })

    return jsonify(result)


@books_bp.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_connection()
    r = conn.execute(
        "SELECT * FROM books WHERE id = ?", (book_id,)
    ).fetchone()
    conn.close()

    if r is None:
        return jsonify({"error": "book not found"}), 404

    return jsonify({
        "id": r[0],
        "title": r[1],
        "author": r[2],
        "isbn": r[3],
        "available": bool(r[4])
    })


@books_bp.route("/books", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}

    if not data.get("title") or not data.get("author"):
        return jsonify({"error": "title and author are required"}), 400

    if not check(data.get("isbn"), "isbn"):
        return jsonify({"error": "invalid isbn"}), 400

    conn = get_connection()

    cur = conn.execute(
        "INSERT INTO books (title, author, isbn, available) VALUES (?, ?, ?, 1)",
        (data["title"], data["author"], data["isbn"])
    )

    conn.commit()

    r = conn.execute(
        "SELECT * FROM books WHERE id = ?", (cur.lastrowid,)
    ).fetchone()

    conn.close()

    return jsonify({
        "id": r[0],
        "title": r[1],
        "author": r[2],
        "isbn": r[3],
        "available": bool(r[4])
    }), 201


@books_bp.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    conn = get_connection()

    r = conn.execute(
        "SELECT * FROM books WHERE id = ?", (book_id,)
    ).fetchone()

    if r is None:
        conn.close()
        return jsonify({"error": "book not found"}), 404

    if r[4] == 0:
        conn.close()
        return jsonify({"error": "book is on loan"}), 409

    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

    return "", 204
