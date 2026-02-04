import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "songs_history.json"

def load_history():
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
    return data.get("songs", [])

def save_song(title, settings, prompt, lyrics=""):
    songs = load_history()
    song = {
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "settings": settings,
        "prompt": prompt,
        "lyrics": lyrics
    }
    songs.append(song)
    with open(HISTORY_FILE, "w") as f:
        json.dump({"songs": songs}, f, indent=2)

def delete_song(index):
    songs = load_history()
    if 0 <= index < len(songs):
        songs.pop(index)
        with open(HISTORY_FILE, "w") as f:
            json.dump({"songs": songs}, f, indent=2)
