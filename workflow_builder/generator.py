"""
Generator functions for building Suno Style and Lyrics field outputs.
"""

from data import AUDIO_QUALITY_TEMPLATE


def build_style_output(genre: str) -> str:
    """
    Build the Style field output with audio quality template.

    Args:
        genre: The genre to insert into the template

    Returns:
        Formatted audio quality prompt for Suno's Style field
    """
    return AUDIO_QUALITY_TEMPLATE.format(genre=genre)


def build_lyrics_output(
    key: str,
    mode: str,
    tempo: str,
    time_sig: str,
    genre: str,
    sections: list[dict],
    lyrics_text: str = ""
) -> str:
    """
    Build the Lyrics field output with [Style] block and meta tags.

    Args:
        key: Selected key (e.g., "C Major")
        mode: Selected mode (e.g., "Dorian")
        tempo: Selected tempo range (e.g., "Mid-tempo (80-110 BPM)")
        time_sig: Selected time signature (e.g., "4/4")
        genre: Selected genre
        sections: List of section dicts with keys: type, instruments
        lyrics_text: Optional lyrics to insert (simple mode)

    Returns:
        Formatted lyrics field content for Suno
    """
    lines = []

    # Build [Style] block
    style_parts = [genre]
    if key:
        style_parts.append(key)
    if mode and mode != "Ionian (Major)":  # Skip default mode
        # Extract just the mode name without parenthetical
        mode_name = mode.split(" (")[0]
        style_parts.append(mode_name)
    if tempo:
        # Extract BPM from tempo string
        style_parts.append(tempo)
    if time_sig and time_sig != "4/4":  # Skip default time sig
        style_parts.append(time_sig)

    lines.append(f"[Style] ({', '.join(style_parts)})")
    lines.append("")

    # Build section meta tags
    for section in sections:
        section_type = section.get("type", "Verse")
        instruments = section.get("instruments", "").strip()

        if instruments:
            lines.append(f"[{section_type}: {instruments}]")
        else:
            lines.append(f"[{section_type}]")

        # Add placeholder for lyrics if not provided
        section_lyrics = section.get("lyrics", "")
        if section_lyrics:
            lines.append(section_lyrics)
            lines.append("")

    # If simple lyrics text provided, append after structure
    if lyrics_text and not any(s.get("lyrics") for s in sections):
        lines.append("")
        lines.append("# Your lyrics:")
        lines.append(lyrics_text)

    return "\n".join(lines)


def build_meta_tag(section_type: str, instruments: str = "") -> str:
    """
    Build a single meta tag string.

    Args:
        section_type: Type of section (Intro, Verse, Chorus, etc.)
        instruments: Optional instrument/mood descriptors

    Returns:
        Formatted meta tag like "[Verse: acoustic guitar, mellow]"
    """
    if instruments:
        return f"[{section_type}: {instruments}]"
    return f"[{section_type}]"
