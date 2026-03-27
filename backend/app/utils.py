"""Utility functions."""

import json


def safe_json(val, default):
    """Handle JSON columns that might be stored as strings in SQLite."""
    if val is None:
        return default
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (ValueError, TypeError):
            return default
    return val
