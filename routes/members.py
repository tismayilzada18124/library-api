
from flask import Blueprint, jsonify, request

from database import get_connection
from helpers import check, money
from datetime import date

members_bp = Blueprint("members", __name__)


@members_bp.route("/members", methods=["GET"])
def list_members():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM members").fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "type": r[3]
        })

    return jsonify(result)


@members_bp.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    conn = get_connection()
    r = conn.execute(
        "SELECT * FROM members WHERE id = ?", (member_id,)
    ).fetchone()
    conn.close()

    if r is None:
        return jsonify({"error": "member not found"}), 404

    return jsonify({
        "id": r[0],
        "name": r[1],
        "email": r[2],
        "type": r[3]
    })


@members_bp.route("/members", methods=["POST"])
def create_member():
    data = request.get_json(silent=True) or {}

    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400

    if not check(data.get("email"), "email"):
        return jsonify({"error": "invalid email"}), 400

    member_type = data.get("type", "student")

    if not check(member_type, "member_type"):
        return jsonify({"error": "type must be student or staff"}), 400

    conn = get_connection()

    existing = conn.execute(
        "SELECT * FROM members WHERE email = ?", (data["email"],)
    ).fetchone()

    if existing is not None:
        conn.close()
        return jsonify({"error": "email already registered"}), 409

    cur = conn.execute(
        "INSERT INTO members (name, email, type) VALUES (?, ?, ?)",
        (data["name"], data["email"], member_type)
    )

    conn.commit()

    r = conn.execute(
        "SELECT * FROM members WHERE id = ?", (cur.lastrowid,)
    ).fetchone()

    conn.close()

    return jsonify({
        "id": r[0],
        "name": r[1],
        "email": r[2],
        "type": r[3]
    }), 201


@members_bp.route("/members/<int:member_id>/loans", methods=["GET"])
def member_loans(member_id):
    conn = get_connection()

    m = conn.execute(
        "SELECT * FROM members WHERE id = ?", (member_id,)
    ).fetchone()

    if m is None:
        conn.close()
        return jsonify({"error": "member not found"}), 404

    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id = ?", (member_id,)
    ).fetchall()

    conn.close()

    owed = 0
    open_loans = 0
    loans = []

    for loan in rows:
        if loan[4] == 0:
            open_loans += 1
            days_late = (date.today() - date.fromisoformat(loan[3])).days

            if days_late > 0:
                owed += days_late * 0.5

        elif loan[6] == 0:
            owed += loan[5]

        loans.append({
            "id": loan[0],
            "book_id": loan[1],
            "due_date": loan[3],
            "returned": bool(loan[4]),
            "fine": money(loan[5]),
            "fine_paid": bool(loan[6])
        })

    if m[3] == "staff":
        remaining = 5 - open_loans
    else:
        remaining = 3 - open_loans

    return jsonify({
        "loans": loans,
        "total_owed": money(owed),
        "loans_remaining": remaining
    })
