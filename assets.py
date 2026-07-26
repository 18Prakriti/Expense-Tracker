"""
Asset configuration for Lumen Expense Tracker
Centralized management of all static resources.
"""

import os

# Project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Assets folder
ASSET_BASE_PATH = os.path.join(BASE_DIR, "assets")

# All image assets
ASSETS = {
    "lumi_main": os.path.join(ASSET_BASE_PATH, "Lumi.png"),
    "dashboard": os.path.join(ASSET_BASE_PATH, "Dashboard.png"),
    "lumi_coach": os.path.join(ASSET_BASE_PATH, "LumiCoach.png"),
    "logo": os.path.join(ASSET_BASE_PATH, "Logo.png"),
    "background": os.path.join(ASSET_BASE_PATH, "Background.png"),
    "login": os.path.join(ASSET_BASE_PATH, "Login.png"),
    "profile": os.path.join(ASSET_BASE_PATH, "Profile.png"),
    "expense": os.path.join(ASSET_BASE_PATH, "Expense.png"),
    "analytics": os.path.join(ASSET_BASE_PATH, "Analytics.png"),
    "reports": os.path.join(ASSET_BASE_PATH, "Reports.png"),
    "settings": os.path.join(ASSET_BASE_PATH, "Settings.png"),
    "notification": os.path.join(ASSET_BASE_PATH, "Notification.png"),
}
