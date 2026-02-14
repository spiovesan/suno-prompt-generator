import re
from data import BASE_PROMPT, STYLE_PRESETS, GUITAR_REPLACE_REMOVE, GUITAR_REPLACE_APPEND

def build_prompt(style_preset="Smooth Jazz", key_signature="", style_influence="",
                 tempo="", mood="", intro="",
                 progression="", harmonic_rhythm="", extensions="",
                 replace_guitar=False):
    """
    Build a Suno prompt with style preset as the foundation.

    Args:
        style_preset: Base style (Bebop, Modal Jazz, Fusion, etc.)
        key_signature: Explicit key (e.g., "in Db major")
        style_influence: Era/style reference (e.g., "70s Electric Funk Jazz")
        tempo: Tempo description
        mood: Mood/atmosphere
        intro: Intro style
        progression: Chord progression type (bracket tags)
        harmonic_rhythm: How often chords change
        extensions: Chord voicing complexity
        replace_guitar: If True, enforce guitar as sole melodic voice
    """
    # Use style preset as the base
    base = STYLE_PRESETS.get(style_preset, BASE_PROMPT)

    # Build additions - key and style influence first, then harmony params (bracket tags)
    additions = [key_signature, style_influence, tempo, mood, intro,
                 progression, harmonic_rhythm, extensions]
    additions = [a for a in additions if a]

    result = base + (", " + ", ".join(additions) if additions else "")

    if replace_guitar:
        for term in GUITAR_REPLACE_REMOVE:
            result = re.sub(re.escape(term), "", result, flags=re.IGNORECASE)
        # Clean up double commas/spaces from removals
        result = re.sub(r",\s*,", ",", result)
        result = re.sub(r"\s{2,}", " ", result)
        result = result.strip(", ")
        result += ", " + GUITAR_REPLACE_APPEND

    return result
