from data import BASE_PROMPT, STYLE_PRESETS

def build_prompt(style_preset="Smooth Jazz", key_signature="", style_influence="",
                 tempo="", mood="", intro="",
                 progression="", harmonic_rhythm="", extensions=""):
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
    """
    # Use style preset as the base
    base = STYLE_PRESETS.get(style_preset, BASE_PROMPT)

    # Build additions - key and style influence first, then harmony params (bracket tags)
    additions = [key_signature, style_influence, tempo, mood, intro,
                 progression, harmonic_rhythm, extensions]
    additions = [a for a in additions if a]

    return base + (", " + ", ".join(additions) if additions else "")
