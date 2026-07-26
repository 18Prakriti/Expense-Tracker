"""
assets.py

Centralized asset management for the Lumen Expense Tracker.
Works locally and after uploading to GitHub or Streamlit Cloud.
"""

from pathlib import Path

# ---------------------------------------------------------
# Project Directories
# ---------------------------------------------------------

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent

# Assets folder
ASSETS_DIR = ROOT_DIR / "assets"

# ---------------------------------------------------------
# Image Assets
# ---------------------------------------------------------

ASSETS = {

    # Main mascot
    "lumi": ASSETS_DIR / "Lumi.png",

    # Dashboard
    "dashboard": ASSETS_DIR / "Dashboard.png",

    # AI Coach
    "coach": ASSETS_DIR / "LumiCoach.png",

    # App logo (if added)
    "logo": ASSETS_DIR / "Logo.png",

    # Login page (if added)
    "login": ASSETS_DIR / "Login.png",

    # Profile page
    "profile": ASSETS_DIR / "Profile.png",

    # Analytics page
    "analytics": ASSETS_DIR / "Analytics.png",

    # Expense page
    "expense": ASSETS_DIR / "Expense.png",

    # Reports page
    "reports": ASSETS_DIR / "Reports.png",

    # Settings page
    "settings": ASSETS_DIR / "Settings.png",

    # Background image
    "background": ASSETS_DIR / "Background.png",

    # Default placeholder
    "placeholder": ASSETS_DIR / "placeholder.png",
}

# ---------------------------------------------------------
# Helper Function
# ---------------------------------------------------------

def asset(name: str) -> str:
    """
    Returns the absolute path of an asset.

    Example:
        st.image(asset("lumi"))
    """
    return str(ASSETS[name])
