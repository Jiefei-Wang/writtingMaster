import json

def load_settings():
    with open("settings.json", "r") as f:
        return json.load(f)