# Description: This file is the entry point of the application. It initializes the database and runs the application.

from shortener import app, db
from shortener.models import User, Link

with app.app_context():
    db.create_all()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    app.run(debug=True)
