"""
Song history storage for Suno Prompt Studio.
Stores generated songs with their settings and outputs.
"""

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / "songs_history.json"


def load_history():
    """Load song history from file."""
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)
    return data.get("songs", [])


def save_song(title: str, settings: dict, style_output: str, lyrics_output: str = ""):
    """
    Save a song to history.

    Args:
        title: Song title
        settings: Dictionary of all settings used
        style_output: Generated Style field output
        lyrics_output: Generated Lyrics field output
    """
    songs = load_history()
    song = {
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "settings": settings,
        "style_output": style_output,
        "lyrics_output": lyrics_output
    }
    songs.append(song)
    with open(HISTORY_FILE, "w") as f:
        json.dump({"songs": songs}, f, indent=2)


def delete_song(index: int):
    """Delete a song from history by index."""
    songs = load_history()
    if 0 <= index < len(songs):
        songs.pop(index)
        with open(HISTORY_FILE, "w") as f:
            json.dump({"songs": songs}, f, indent=2)


def export_history_csv() -> str:
    """Export history as CSV format string."""
    songs = load_history()
    if not songs:
        return ""

    lines = ["Title,Timestamp,Genre,Style Output,Lyrics Output"]
    for song in songs:
        title = song.get("title", "").replace(",", ";")
        timestamp = song.get("timestamp", "")
        genre = song.get("settings", {}).get("genre", "").replace(",", ";")
        style = song.get("style_output", "").replace(",", ";").replace("\n", " ")[:200]
        lyrics = song.get("lyrics_output", "").replace(",", ";").replace("\n", " ")[:200]
        lines.append(f'"{title}","{timestamp}","{genre}","{style}...","{lyrics}..."')

    return "\n".join(lines)
