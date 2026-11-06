from datetime import date
from flask import Blueprint, jsonify

from database import get_connection
from helpers import money
from services import calculate_fine

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports/overdue", methods=["GET"])
def report_overdue():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT loans.id, books.title, members.name, loans.due_date
        FROM loans
        JOIN books ON books.id = loans.book_id
        JOIN members ON members.id = loans.member_id
        WHERE loans.returned = 0
        """
    ).fetchall()

    conn.close()

    items = []
    total = 0

    for r in rows:
        days_late = (date.today() - date.fromisoformat(r[3])).days

        if days_late > 0:
            fine = calculate_fine(days_late)
            total += fine

            items.append({
                "loan_id": r[0],
                "title": r[1],
                "member": r[2],
                "days_late": days_late,
                "fine": money(fine)
            })

    return jsonify({
        "items": items,
        "total_fines": money(total)
    })


@reports_bp.route("/reports/summary", methods=["GET"])
def report_summary():
    conn = get_connection()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    rows = conn.execute(
        "SELECT * FROM loans"
    ).fetchall()

    conn.close()

    on_loan = 0
    outstanding = 0

    for loan in rows:
        if loan[4] == 0:
            on_loan += 1

            days_late = (
                date.today() - date.fromisoformat(loan[3])
            ).days

            outstanding += calculate_fine(days_late)

        elif loan[6] == 0:
            outstanding += loan[5]

    return jsonify({
        "total_books": total_books,
        "on_loan": on_loan,
        "fines_outstanding": money(outstanding)
    })