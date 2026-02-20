import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"watch_directory": "", "categories": {}, "handle_duplicates": True}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

CONFIG = load_config()
WATCH_DIR = CONFIG.get("watch_directory", "")
FILE_CATEGORIES = CONFIG.get("categories", {})
HANDLE_DUPLICATES = CONFIG.get("handle_duplicates", True)

def save_config(config_dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_dict, f, indent=4)
