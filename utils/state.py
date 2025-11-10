import json

def read_state_codes():
    """Read state codes from codes.json"""
    try:
        with open('codes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}