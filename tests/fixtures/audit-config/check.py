import json
from pathlib import Path

assert json.loads(Path("settings.json").read_text())["port"] == 8080
print("port matches release requirement")
