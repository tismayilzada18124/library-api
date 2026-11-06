import os

from flask import Flask

from database import init_db
from routes.books import books_bp
from routes.members import members_bp
from routes.loans import loans_bp
from routes.reports import reports_bp


app = Flask(__name__)


app.register_blueprint(books_bp)
app.register_blueprint(members_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(reports_bp)


if not os.path.exists("library.db"):
    init_db()


if __name__ == "__main__":
    app.run(debug=True)