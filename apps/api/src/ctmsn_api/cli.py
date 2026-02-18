from __future__ import annotations

import argparse
import sys

from ctmsn_api.auth import hash_password
from ctmsn_api.database import SessionLocal, create_tables
from ctmsn_api.models import Role, User


def create_teacher(username: str, password: str) -> None:
    create_tables()
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == username).first():
            print(f"Error: user '{username}' already exists", file=sys.stderr)
            sys.exit(1)

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=Role.teacher,
        )
        db.add(user)
        db.commit()
        print(f"Teacher '{username}' created successfully")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="ctmsn-admin", description="CTMSN admin CLI")
    sub = parser.add_subparsers(dest="command")

    ct = sub.add_parser("create-teacher", help="Create a teacher account")
    ct.add_argument("--username", required=True)
    ct.add_argument("--password", required=True)

    args = parser.parse_args()

    if args.command == "create-teacher":
        create_teacher(args.username, args.password)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
