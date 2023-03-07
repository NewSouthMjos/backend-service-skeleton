#!/bin/bash
# PATH="/app/venv/bin:$PATH"
# alembic upgrade head
python3 migrate.py
exec python3 __main__.py