"""Presentation helpers for PawPal+ output: category emojis and priority indicators.

Kept separate from pawpal_system.py so the logic layer stays free of display concerns;
both main.py (CLI) and app.py (Streamlit) import from here.
"""

CATEGORY_EMOJIS = {
    "walk": "🚶",
    "feeding": "🍖",
    "meds": "💊",
    "enrichment": "🎾",
    "grooming": "🧼",
}

PRIORITY_INDICATORS = {
    "high": "🔴 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}

STATUS_EMOJIS = {
    True: "✅",
    False: "⬜",
}


def category_label(category: str) -> str:
    """Return a category name prefixed with its emoji, e.g. "🚶 walk"."""
    return f"{CATEGORY_EMOJIS.get(category, '📋')} {category}"


def priority_label(priority: str) -> str:
    """Return a color-coded priority indicator, e.g. "🔴 HIGH"."""
    return PRIORITY_INDICATORS.get(priority, f"⚪ {priority.upper()}")


def status_emoji(completed: bool) -> str:
    """Return a checkmark/blank-box emoji for a task's completion status."""
    return STATUS_EMOJIS[completed]
