import os

BASE_URL = os.getenv("GITEA_URL", "http://localhost:3000").rstrip("/")
ADMIN_USER = os.getenv("GITEA_ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("GITEA_ADMIN_PASS", "Admin123!pass")

# HEADLESS=0 uruchamia przeglądarkę w trybie widocznym (demo)
HEADLESS = os.getenv("HEADLESS", "1") != "0"
BROWSER = os.getenv("BROWSER", "chrome")
DEFAULT_TIMEOUT = float(os.getenv("UI_TIMEOUT", "10"))
WINDOW_SIZE = (1440, 900)
