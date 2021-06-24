import json
def open_json(path):
    f = open(path)
    loaded_json = json.load(f)
    return loaded_json