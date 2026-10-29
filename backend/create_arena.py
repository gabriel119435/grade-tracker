import argparse
import os
import sys

# adds backend/ to import search path
sys.path.insert(0, os.path.dirname(__file__))

from app.arena import create_arena
from app.migrations import apply_migrations


def main():
    """
    creates a new arena and its only admin directly in the db, the only way to add an arena.

    usage: uv run create_arena.py <arena> <admin> <password>
    """
    parser = argparse.ArgumentParser(description="creates a new arena and its admin")
    parser.add_argument("arena")
    parser.add_argument("admin")
    parser.add_argument("password")
    args = parser.parse_args()

    # a run before the first app start finds no tables
    apply_migrations()

    try:
        created = create_arena(args.arena, args.admin, args.password)
    except ValueError as e:
        print(e)
        sys.exit(1)

    if not created:
        print("arena_already_exists")
        sys.exit(1)

    print("success")


if __name__ == "__main__":
    main()
