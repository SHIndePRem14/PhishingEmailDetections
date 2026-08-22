"""Creates (or promotes) an administrator account.

Usage:
    python scripts/create_admin.py
Then follow the interactive prompts.
"""

import os
import sys
import getpass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from app import create_app, db  # noqa: E402
from app.models.user import User  # noqa: E402


def main():
    app = create_app(os.environ.get("FLASK_ENV", "development"))

    with app.app_context():
        print("=== PhishGuard: Create Admin Account ===")
        name = input("Full name: ").strip()
        email = input("Email: ").strip().lower()
        password = getpass.getpass("Password (min 8 chars): ")

        if len(password) < 8:
            print("Password must be at least 8 characters. Aborting.")
            return

        existing = User.query.filter_by(email=email).first()
        if existing:
            existing.role = "admin"
            existing.set_password(password)
            db.session.commit()
            print(f"Existing user '{email}' promoted to admin and password updated.")
            return

        admin = User(name=name, email=email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin account created: {email}")


if __name__ == "__main__":
    main()
