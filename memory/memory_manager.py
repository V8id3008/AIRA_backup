import json

PROFILE_FILE = "data/profile.json"
MEMORY_FILE = "data/memory.json"

def load_profile():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
import json

MEMORY_FILE = "data/memory.json"

def load_memory():

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    except:
        return {"memories": []}

def save_memory(memory):

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def add_memory(item):

    memory = load_memory()

    memory["memories"].append(item)

    save_memory(memory)