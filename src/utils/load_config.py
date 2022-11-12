import json

def get_json():
    with open("./config.json", "r") as f:
        return json.load(f)