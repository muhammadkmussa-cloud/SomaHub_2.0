"""Backward-compatible entry point — prefer `app.main:app`."""

from app.main import app

__all__ = ["app"]
