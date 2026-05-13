default:
    @just --list

qa:
    uv run ruff check
    uv run ruff format --check
    uv run mypy
    uv run pytest

qa-auto-fix:
    uv run ruff check --fix
    uv run ruff format
    uv run mypy
    uv run pytest
