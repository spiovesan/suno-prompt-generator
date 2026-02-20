"""
Generation engine for Suno Prompt Studio.

Preset as foundation: Style field starts with a detailed preset, then parameters
are appended. Harmony bracket tags go in the Style field. Lyrics field contains
only [Style] block + [Section: instruments] tags. Clean output only — positive
descriptors, no clutter.
"""

import os
import re
import json
import random
import hashlib
from openai import OpenAI
from cache import get_cached, set_cached
from data import (
    STYLE_PRESETS, STYLE_INFLUENCES, BASE_PROMPT,
    resolve_preset_value, resolve_influence_value,
    GUITAR_REPLACE_REMOVE, GUITAR_REPLACE_APPEND, LYRIC_TEMPLATES
)
from profiles import DEV_STYLE_PRESETS


# =============================================================================
# CONSTANTS
# =============================================================================

MAX_STYLE_LENGTH = 1000


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

JAZZ_SYSTEM_PROMPT = """You are a Suno AI music prompt specialist. Generate a coherent, well-crafted music prompt that combines all the user's selections harmoniously.

## HARD CONSTRAINTS (NEVER VIOLATE):
- QUARTET ONLY: guitar, piano, bass, drums - NO saxophone, brass, strings, vocals, or other instruments
- GUITAR IS LEAD: Guitar plays melody/theme, piano provides harmonic support only
- NO NEGATIVE TERMS: Never use "no", "without", "don't" - Suno ignores negatives
- NO ARTIST NAMES: Never use musician names (no Coltrane, Metheny, Scofield, etc.) - Suno blocks these
- UNDER 200 WORDS: Keep prompts concise
- COMMA-SEPARATED: Use comma-separated descriptors
- LYRICS FIELD IS SEPARATE: If a lyric template is mentioned, it informs the aesthetic but do NOT include lyrics content in the style prompt
- GUITAR REPLACEMENT MODE: When the user indicates they will replace the guitar stem, ensure guitar is ALWAYS the primary melodic voice. Piano, bass, drums provide ONLY harmonic and rhythmic support.

## COHERENCE RULES:
- If mood is "Intimate" or "Mellow", use clean guitar tones, brushed drums, soft dynamics
- If mood is "Energetic" or "Dark", allow more aggressive tones but still respect tempo
- Slow tempos (60-80 BPM) should have spacious arrangements
- Fast tempos allow driving energy and complex passages

## HARMONY RULES:
- NEVER use simple IVm7-Im7 or VIm7-IVmaj7 loops
- Include bracket tags for chord control when harmony params specified
- Default to [complex chord progression, jazz influences]

Return ONLY the prompt text, no explanations or formatting. Use comma-separated descriptors."""


UNIVERSAL_SYSTEM_PROMPT = """You are a Suno AI music prompt specialist for diverse genres. Generate a coherent, well-crafted music prompt.

## HARD CONSTRAINTS:
- NO NEGATIVE TERMS: Never use "no", "without", "don't" - Suno ignores negatives. Only describe what you WANT.
- NO ARTIST NAMES: Suno blocks these
- UNDER 200 WORDS: Keep prompts concise
- COMMA-SEPARATED: Use comma-separated descriptors
- EXPLICIT INSTRUMENT ROLES: Name specific instruments with their roles (e.g., "warm pad synths provide atmosphere, crisp hi-hats drive rhythm")
- Include bracket tags when harmony parameters are specified

## COHERENCE RULES:
- Match instrumentation to genre conventions
- Match dynamics/energy to mood and tempo
- Be specific about production quality and sound design

Always include some production descriptors:
- Sound quality: "studio quality", "well mastered", "clean mix", "warm presence"
- Dynamics: "dynamic contrast", "building intensity", "subtle dynamics"

Return ONLY the prompt text, no explanations or formatting. Use comma-separated descriptors."""


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def generate_outputs(
    genre: str,
    key: str = "",
    mode: str = "",
    tempo: str = "",
    time_sig: str = "",
    mood: str = "",
    sections: list = None,
    suno_lyrics: str = "",
    lyric_template: str = "None",
    style_preset: str = "",
    style_influence: str = "",
    progression: str = "",
    harmonic_rhythm: str = "",
    extensions: str = "",
    replace_guitar: bool = False,
    use_llm: bool = False,
    api_key: str = None,
    profile: str = "General Purpose",
    tech_context: str = "",
    # Accepted for backward compatibility, not used in output
    instrumental: bool = False,
    ensemble: str = "",
    **kwargs,
) -> dict:
    """
    Generate Style and Lyrics outputs for Suno.

    For Jazz: preset as foundation + optional LLM generation.
    For other genres: genre + preset + influence + harmony + hints + quality.

    Returns:
        {"style": str, "lyrics": str, "cached": bool}
    """
    sections = sections or []
    cached = False

    # Extract section-based style hints for Style field reinforcement
    section_style_hints = _extract_section_style_hints(sections)

    # ── STYLE FIELD ──────────────────────────────────────────────────────
    if genre == "Jazz":
        if use_llm and api_key:
            result = _generate_jazz_llm(
                style_preset=style_preset,
                key=key,
                style_influence=style_influence,
                tempo=tempo,
                mood=mood,
                progression=progression,
                harmonic_rhythm=harmonic_rhythm,
                extensions=extensions,
                lyric_template=lyric_template,
                replace_guitar=replace_guitar,
                sections=sections,
                api_key=api_key,
            )
            style_output = result["prompt"]
            cached = result["cached"]
        else:
            style_output = _generate_jazz_static(
                style_preset=style_preset,
                key=key,
                style_influence=style_influence,
                tempo=tempo,
                mood=mood,
                progression=progression,
                harmonic_rhythm=harmonic_rhythm,
                extensions=extensions,
                replace_guitar=replace_guitar,
            )
            # Append section hints for static mode
            if section_style_hints:
                style_output += ", " + section_style_hints
    else:
        # Universal mode — all non-Jazz genres
        if use_llm and api_key:
            result = _generate_universal_llm(
                genre=genre,
                key=key,
                mode=mode,
                tempo=tempo,
                mood=mood,
                style_preset=style_preset,
                style_influence=style_influence,
                progression=progression,
                harmonic_rhythm=harmonic_rhythm,
                extensions=extensions,
                sections=sections,
                api_key=api_key,
                tech_context=tech_context,
                profile=profile,
            )
            style_output = result["prompt"]
            cached = result["cached"]
        else:
            # Static template-based generation
            style_parts = [genre]

            # Preset value (the musical description, not just the name)
            if style_preset and style_preset != "None":
                if profile == "Developer Focus" and style_preset in DEV_STYLE_PRESETS:
                    preset_value = DEV_STYLE_PRESETS[style_preset]
                else:
                    preset_value = resolve_preset_value(style_preset, genre)
                if preset_value:
                    style_parts.append(preset_value)

            # Style influence
            if style_influence and style_influence != "None":
                influence_value = resolve_influence_value(style_influence, genre)
                if influence_value:
                    style_parts.append(influence_value)

            # Harmony bracket tags go directly in the Style field
            harmony_tags = [h for h in [progression, harmonic_rhythm, extensions]
                            if h and h != "None" and h.strip()]
            for tag in harmony_tags:
                style_parts.append(tag)

            # Music foundation hints (key, mode, tempo, mood, time sig)
            music_hints = _build_music_foundation_hints(
                key=key, mode=mode, tempo=tempo, mood=mood, time_sig=time_sig
            )
            if music_hints:
                style_parts.append(music_hints)

            # Section style hints
            if section_style_hints:
                style_parts.append(section_style_hints)

            # Audio quality tail
            style_parts.append(
                "studio quality, well mastered, clean mix, warm presence, crisp highs"
            )

            style_output = ", ".join(style_parts)

    # ── LYRICS FIELD ─────────────────────────────────────────────────────
    lyrics_output = _build_lyrics_output(
        genre=genre,
        key=key,
        mode=mode,
        tempo=tempo,
        time_sig=time_sig,
        sections=sections,
        suno_lyrics=suno_lyrics,
        lyric_template=lyric_template,
    )

    # ── TRUNCATE STYLE ───────────────────────────────────────────────────
    if len(style_output) > MAX_STYLE_LENGTH:
        truncated = style_output[:MAX_STYLE_LENGTH]
        last_comma = truncated.rfind(", ")
        if last_comma > MAX_STYLE_LENGTH // 2:
            style_output = truncated[:last_comma]
        else:
            style_output = truncated.rstrip(", ")

    return {
        "style": style_output,
        "lyrics": lyrics_output,
        "cached": cached,
    }


# =============================================================================
# JAZZ STATIC — preset as foundation + comma-separated additions
# =============================================================================

def _generate_jazz_static(
    style_preset: str,
    key: str,
    style_influence: str,
    tempo: str,
    mood: str,
    progression: str,
    harmonic_rhythm: str,
    extensions: str,
    replace_guitar: bool,
) -> str:
    """Generate jazz prompt using static concatenation (legacy approach)."""
    base = STYLE_PRESETS.get(style_preset, BASE_PROMPT)

    additions = [
        key,
        style_influence,
        tempo,
        mood,
        progression,
        harmonic_rhythm,
        extensions,
    ]
    additions = [a for a in additions if a and a != "None"]

    result = base + (", " + ", ".join(additions) if additions else "")

    if replace_guitar:
        result = _apply_guitar_replacement(result)

    return result


# =============================================================================
# JAZZ LLM
# =============================================================================

def _generate_jazz_llm(
    style_preset: str,
    key: str,
    style_influence: str,
    tempo: str,
    mood: str,
    progression: str,
    harmonic_rhythm: str,
    extensions: str,
    lyric_template: str,
    replace_guitar: bool,
    sections: list,
    api_key: str,
) -> dict:
    """Generate jazz prompt using LLM. Returns {"prompt": str, "cached": bool}."""
    section_hints = _extract_section_style_hints(sections)

    selections = {
        "style_preset": style_preset,
        "key_signature": key,
        "style_influence": style_influence,
        "tempo": tempo,
        "mood": mood,
        "progression": progression,
        "harmonic_rhythm": harmonic_rhythm,
        "extensions": extensions,
        "lyric_template": lyric_template,
        "replace_guitar": replace_guitar,
        "section_hints": section_hints,
    }

    cache_key = hashlib.md5(
        json.dumps(selections, sort_keys=True).encode()
    ).hexdigest()

    cached = get_cached(cache_key)
    if cached:
        return {"prompt": cached, "cached": True}

    user_msg = _build_jazz_llm_message(selections)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JAZZ_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    prompt = response.choices[0].message.content.strip()
    set_cached(cache_key, prompt)

    return {"prompt": prompt, "cached": False}


def _build_jazz_llm_message(selections: dict) -> str:
    """Build user message for jazz LLM from selections dict."""
    parts = []

    if selections.get("style_preset") and selections["style_preset"] != "None":
        parts.append(f"Style: {selections['style_preset']}")

    if selections.get("key_signature") and selections["key_signature"] != "None":
        parts.append(f"Key: {selections['key_signature']}")

    if selections.get("style_influence") and selections["style_influence"] != "None":
        parts.append(f"Influence: {selections['style_influence']}")

    if selections.get("tempo") and selections["tempo"] != "None":
        parts.append(f"Tempo: {selections['tempo']}")

    if selections.get("mood") and selections["mood"] != "None":
        parts.append(f"Mood: {selections['mood']}")

    if selections.get("progression") and selections["progression"] != "None":
        parts.append(f"Chord Progression: {selections['progression']}")

    if selections.get("harmonic_rhythm") and selections["harmonic_rhythm"] != "None":
        parts.append(f"Harmonic Rhythm: {selections['harmonic_rhythm']}")

    if selections.get("extensions") and selections["extensions"] != "None":
        parts.append(f"Chord Extensions: {selections['extensions']}")

    if selections.get("lyric_template") and selections["lyric_template"] != "None":
        parts.append(
            f"Aesthetic context: {selections['lyric_template']} "
            "(do NOT include lyrics in output)"
        )

    if selections.get("replace_guitar"):
        parts.append(
            "IMPORTANT: User will replace the guitar stem. Guitar MUST be the "
            "only melodic voice. Piano/bass/drums provide only support."
        )

    if selections.get("section_hints"):
        parts.append(
            f"Song features: {selections['section_hints']} "
            "(include these characteristics in prompt)"
        )

    if not parts:
        return (
            "Generate a default smooth jazz quartet prompt with guitar lead "
            "and [complex chord progression]"
        )

    return "Generate a Suno prompt for:\n" + "\n".join(parts)


# =============================================================================
# UNIVERSAL LLM — for non-Jazz genres
# =============================================================================

def _generate_universal_llm(
    genre: str,
    key: str,
    mode: str,
    tempo: str,
    mood: str,
    style_preset: str,
    style_influence: str,
    progression: str,
    harmonic_rhythm: str,
    extensions: str,
    sections: list,
    api_key: str,
    tech_context: str = "",
    profile: str = "General Purpose",
) -> dict:
    """Generate prompt for any non-Jazz genre using LLM."""
    section_hints = _extract_section_style_hints(sections)

    # Resolve developer preset value if applicable
    resolved_preset = style_preset
    if profile == "Developer Focus" and style_preset in DEV_STYLE_PRESETS:
        resolved_preset = f"{style_preset} ({DEV_STYLE_PRESETS[style_preset]})"

    selections = {
        "genre": genre,
        "key_signature": key,
        "mode": mode,
        "tempo": tempo,
        "mood": mood,
        "style_preset": resolved_preset,
        "style_influence": style_influence,
        "progression": progression,
        "harmonic_rhythm": harmonic_rhythm,
        "extensions": extensions,
        "section_hints": section_hints,
        "tech_context": tech_context,
    }

    cache_key = "universal_" + hashlib.md5(
        json.dumps(selections, sort_keys=True).encode()
    ).hexdigest()

    cached = get_cached(cache_key)
    if cached:
        return {"prompt": cached, "cached": True}

    user_msg = _build_universal_llm_message(selections)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": UNIVERSAL_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=500,
        temperature=0.7,
    )

    prompt = response.choices[0].message.content.strip()
    set_cached(cache_key, prompt)

    return {"prompt": prompt, "cached": False}


def _build_universal_llm_message(selections: dict) -> str:
    """Build user message for universal LLM from selections dict."""
    parts = []

    parts.append(f"Genre: {selections['genre']}")

    if selections.get("style_preset") and selections["style_preset"] != "None":
        parts.append(f"Style preset: {selections['style_preset']}")

    if selections.get("key_signature") and selections["key_signature"] != "None":
        parts.append(f"Key: {selections['key_signature']}")

    if (selections.get("mode")
            and selections["mode"] != "None"
            and selections["mode"] != "Ionian (Major)"):
        parts.append(f"Mode: {selections['mode']}")

    if selections.get("style_influence") and selections["style_influence"] != "None":
        parts.append(f"Influence: {selections['style_influence']}")

    if selections.get("tempo") and selections["tempo"] != "None":
        parts.append(f"Tempo: {selections['tempo']}")

    if selections.get("mood") and selections["mood"] != "None":
        parts.append(f"Mood: {selections['mood']}")

    if (selections.get("progression")
            and selections["progression"] != "None"
            and selections["progression"].strip()):
        parts.append(f"Chord progression: {selections['progression']}")

    if (selections.get("harmonic_rhythm")
            and selections["harmonic_rhythm"] != "None"
            and selections["harmonic_rhythm"].strip()):
        parts.append(f"Harmonic rhythm: {selections['harmonic_rhythm']}")

    if (selections.get("extensions")
            and selections["extensions"] != "None"
            and selections["extensions"].strip()):
        parts.append(f"Chord extensions: {selections['extensions']}")

    if selections.get("section_hints"):
        parts.append(
            f"Song features: {selections['section_hints']} "
            "(include these characteristics in prompt)"
        )

    if selections.get("tech_context"):
        parts.append(
            f"Context: This is background music for a developer working on: "
            f"{selections['tech_context']}. "
            "Subtly adjust the mood to match this creative context."
        )

    return "Generate a Suno music prompt for:\n" + "\n".join(parts)


# =============================================================================
# LYRICS OUTPUT — clean: [Style] block + [Section: instruments] tags
# =============================================================================

def _build_lyrics_output(
    genre: str,
    key: str,
    mode: str,
    tempo: str,
    time_sig: str,
    sections: list,
    suno_lyrics: str,
    lyric_template: str,
) -> str:
    """
    Build the Lyrics field output.

    Structure:
        [Style] (genre, key, mode, tempo, time_sig)
        <blank line>
        [Section: instruments]
        <lyrics if available>
        ...
    """
    lines = []

    # ── [Style] block ────────────────────────────────────────────────────
    style_parts = [genre]
    if key and key != "None":
        style_parts.append(key)
    if mode and mode != "Ionian (Major)" and mode != "None":
        mode_name = mode.split(" (")[0] if " (" in mode else mode
        style_parts.append(mode_name)
    if tempo and tempo != "None":
        style_parts.append(tempo)
    if time_sig and time_sig != "4/4" and time_sig != "None":
        style_parts.append(time_sig)

    lines.append(f"[Style] ({', '.join(style_parts)})")
    lines.append("")

    # ── Lyric template takes priority (replaces section structure) ───────
    # Templates like "Anti-Listening" have their own custom section names
    # (e.g. [Opening Field], [Primary Material]) that are incompatible with
    # standard Suno tags. Using both causes "two songs in one" conflicts.
    if lyric_template and lyric_template != "None":
        template = LYRIC_TEMPLATES.get(lyric_template, "")
        if template:
            lines.append(template)
            return "\n".join(lines).strip()

    # ── Parse pasted lyrics ──────────────────────────────────────────────
    parsed_lyrics = _parse_suno_lyrics(suno_lyrics) if suno_lyrics else {}
    section_counters = {}  # tracks how many blocks consumed per key
    consumed_keys = set()  # tracks which keys had ANY block consumed

    # ── Merge: structure sections + matching pasted lyrics ────────────────
    for section in (sections or []):
        section_type = section.get("type", "Verse")
        instruments = section.get("instruments", "").strip()

        if instruments:
            lines.append(f"[{section_type}: {instruments}]")
        else:
            lines.append(f"[{section_type}]")

        # Try to pull matching lyrics content from paste
        section_key = section_type.lower()
        matched_key = None

        if section_key in parsed_lyrics:
            matched_key = section_key
        elif parsed_lyrics:
            matched_key = _get_nearest_section_type(
                section_key, set(parsed_lyrics.keys())
            )

        if matched_key and matched_key in parsed_lyrics:
            counter = section_counters.get(matched_key, 0)
            blocks = parsed_lyrics[matched_key]
            if counter < len(blocks):
                content = blocks[counter]["content"]
                if content:
                    lines.append(content)
                section_counters[matched_key] = counter + 1
                consumed_keys.add(matched_key)

        lines.append("")

    # ── Append lyrics-only sections (not in structure editor) ─────────────
    for key, blocks in parsed_lyrics.items():
        if key in consumed_keys:
            # Append any remaining blocks beyond what was consumed
            start = section_counters.get(key, 0)
            for block in blocks[start:]:
                lines.append(block["tag"])
                if block["content"]:
                    lines.append(block["content"])
                lines.append("")
        else:
            # Key never matched any structure section — keep all blocks
            for block in blocks:
                lines.append(block["tag"])
                if block["content"]:
                    lines.append(block["content"])
                lines.append("")

    return "\n".join(lines).strip()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _apply_guitar_replacement(prompt: str) -> str:
    """Apply guitar replacement filtering."""
    result = prompt
    for term in GUITAR_REPLACE_REMOVE:
        result = re.sub(re.escape(term), "", result, flags=re.IGNORECASE)
    result = re.sub(r",\s*,", ",", result)
    result = re.sub(r"\s{2,}", " ", result)
    result = result.strip(", ")
    result += ", " + GUITAR_REPLACE_APPEND
    return result


def _extract_section_style_hints(sections: list) -> str:
    """Extract instrument/style keywords from sections for Style field reinforcement."""
    if not sections:
        return ""
    hints = set()
    for s in sections:
        inst = s.get("instruments", "").strip()
        if inst:
            for part in inst.split(","):
                part = part.strip().lower()
                if len(part) > 3 and part not in ("none",):
                    hints.add(part)
    return ", ".join(sorted(hints)[:5]) if hints else ""


def _build_music_foundation_hints(
    key: str = "",
    mode: str = "",
    tempo: str = "",
    mood: str = "",
    time_sig: str = "",
) -> str:
    """Build concise music foundation string for Style field."""
    hints = []

    if key and key != "None":
        hints.append(f"in {key}")

    if mode and mode != "Ionian (Major)" and mode != "None":
        mode_name = mode.split(" (")[0] if " (" in mode else mode
        hints.append(f"{mode_name} mode")

    if tempo and tempo != "None":
        if "(" in tempo and ")" in tempo:
            label = tempo[:tempo.index("(")].strip().lower()
            bpm = tempo[tempo.index("(") + 1:tempo.index(")")]
            hints.append(f"{label}, {bpm}")
        else:
            hints.append(tempo.lower())

    if mood and mood != "None":
        hints.append(f"{mood} mood")

    if time_sig and time_sig != "4/4" and time_sig != "None":
        hints.append(f"{time_sig} time")

    return ", ".join(hints)


def _parse_suno_lyrics(text: str) -> dict:
    """
    Parse Suno-format lyrics into {section_key: [{"tag": str, "content": str}]}.

    Handles tags like [Verse], [Chorus], [Verse 2], [Solo: guitar].
    Returns lowercase keys mapping to lists of dicts with original tag and content.
    """
    if not text or not text.strip():
        return {}

    result = {}
    current_section = None
    current_tag_line = None
    current_lines = []

    for line in text.strip().split("\n"):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if current_section:
                content = "\n".join(current_lines).strip()
                result.setdefault(current_section, []).append(
                    {"tag": current_tag_line, "content": content}
                )
            tag = stripped[1:-1].split(":")[0].strip().lower()
            # Normalize numbered sections: "verse 2" -> "verse"
            tag = re.sub(r"\s*\d+$", "", tag).strip()
            current_section = tag
            current_tag_line = stripped
            current_lines = []
        elif current_section is not None:
            current_lines.append(line)

    if current_section:
        content = "\n".join(current_lines).strip()
        result.setdefault(current_section, []).append(
            {"tag": current_tag_line, "content": content}
        )

    return result


def _get_nearest_section_type(section_type: str, available_types: set) -> str:
    """
    Find nearest matching section type for unmapped lyrics.

    Conservative: only maps true synonyms (hook <-> chorus, refrain <-> chorus).
    Returns None if no match found — section stays without lyrics.
    """
    section_type = section_type.lower()

    if section_type in available_types:
        return section_type

    SYNONYMS = {
        "hook": ["chorus", "refrain"],
        "refrain": ["chorus", "hook"],
        "chorus": ["hook", "refrain"],
    }

    if section_type in SYNONYMS:
        for synonym in SYNONYMS[section_type]:
            if synonym in available_types:
                return synonym

    return None


def parse_lyrics_to_sections(lyrics_text: str) -> list:
    """
    Parse pasted Suno lyrics and return section list for Song Structure.

    Extracts section tags from pasted lyrics and returns them in a format
    suitable for the Song Structure editor.

    Returns:
        List of section dicts: [{"id": "...", "type": "Verse", "instruments": ""}, ...]
    """
    if not lyrics_text or not lyrics_text.strip():
        return []

    import uuid

    sections = []
    tag_pattern = re.compile(r'\[([^\]:]+)(?::\s*([^\]]+))?\]', re.IGNORECASE)

    for match in tag_pattern.finditer(lyrics_text):
        section_type = match.group(1).strip()
        instruments = match.group(2).strip() if match.group(2) else ""

        # Normalize: "Verse 1" -> "Verse", "CHORUS" -> "Chorus"
        normalized_type = re.sub(r'\s*\d+$', '', section_type).strip()
        normalized_type = normalized_type.title()

        # Skip non-section tags
        if normalized_type.lower() in ('style', 'end'):
            continue

        sections.append({
            "id": str(uuid.uuid4()),
            "type": normalized_type,
            "instruments": instruments,
        })

    return sections


# =============================================================================
# LYRICS VALIDATION
# =============================================================================

STANDARD_SUNO_TAGS = {
    "intro", "verse", "chorus", "pre-chorus", "prechorus", "bridge",
    "outro", "hook", "drop", "breakdown", "buildup", "build",
    "solo", "instrumental", "interlude", "break", "refrain",
    "style", "end",
}


def validate_lyrics_format(lyrics_text: str) -> dict:
    """
    Validate Suno lyrics format. Returns {valid: bool, issues: list}.

    Also performs deeper analysis including tag counts, non-standard tags,
    and length checks.
    """
    if not lyrics_text or not lyrics_text.strip():
        return {
            "valid": True,
            "issues": [],
            "warnings": [],
            "suggestions": ["Add song structure with section tags like [Intro], [Verse], [Chorus]"],
            "tag_analysis": {},
        }

    issues = []
    warnings = []
    suggestions = []

    lines = lyrics_text.strip().split("\n")
    has_section = any(l.strip().startswith("[") for l in lines)
    if not has_section:
        issues.append("No section tags found (e.g., [Verse], [Chorus])")

    if len(lyrics_text) > 3000:
        issues.append(f"Lyrics too long ({len(lyrics_text)} chars, max 3000)")

    # Extract all bracket tags
    tag_pattern = re.compile(r'\[([^\]]+)\]', re.IGNORECASE)
    all_tags = tag_pattern.findall(lyrics_text)

    standard_tags = []
    custom_tags = []
    tag_counts = {}

    for tag in all_tags:
        base_tag = tag.split(":")[0].strip().lower()
        base_tag_normalized = re.sub(r'\s*\d+$', '', base_tag).strip()

        tag_counts[base_tag_normalized] = tag_counts.get(base_tag_normalized, 0) + 1

        if base_tag_normalized in STANDARD_SUNO_TAGS:
            standard_tags.append(tag)
        else:
            custom_tags.append(tag)

    # Check for duplicate structures
    structure_like_customs = []
    for tag in custom_tags:
        base = tag.split(":")[0].strip().lower()
        if any(kw in base for kw in ["field", "section", "part", "material", "movement"]):
            structure_like_customs.append(tag)

    # Only warn if BOTH sides have substantial structure (4+ standard tags
    # alongside custom structure tags). A few standard tags like [Outro] mixed
    # into a custom-structured template is normal, not a duplicate.
    if len(standard_tags) >= 4 and structure_like_customs:
        warnings.append(
            f"Duplicate song structures detected! You have standard Suno tags "
            f"({len(standard_tags)} tags) AND custom structure tags "
            f"({len(structure_like_customs)} tags like [{structure_like_customs[0]}]). "
            f"This may cause Suno to create two songs in one."
        )
        suggestions.append(
            "Use ONLY standard Suno tags and put descriptive content "
            "inside them as parenthetical hints."
        )

    # Non-standard tags
    if custom_tags and not structure_like_customs:
        non_standard_list = list(set(
            [t.split(":")[0].strip() for t in custom_tags[:5]]
        ))
        if non_standard_list:
            warnings.append(
                f"Non-standard tags detected: [{'], ['.join(non_standard_list)}]. "
                f"Suno may not recognize these as sections."
            )

    # Check for [Style] block
    has_style = any(t.lower().startswith("style") for t in all_tags)
    if not has_style:
        suggestions.append(
            "Consider adding a [Style] block at the top for genre/key/tempo info."
        )

    # Check for empty sections
    for i, line in enumerate(lines):
        if tag_pattern.match(line.strip()):
            for j in range(i + 1, min(i + 3, len(lines))):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('('):
                    if tag_pattern.match(next_line):
                        tag_name = tag_pattern.match(line.strip()).group(1)
                        suggestions.append(
                            f"Section [{tag_name}] has no content. "
                            "Consider adding descriptive hints."
                        )
                    break

    return {
        "valid": len(issues) == 0 and len(warnings) == 0,
        "issues": issues,
        "warnings": warnings,
        "suggestions": suggestions,
        "tag_analysis": {
            "total_tags": len(all_tags),
            "standard_tags": len(standard_tags),
            "custom_tags": len(custom_tags),
            "tag_counts": tag_counts,
        },
    }


def validate_lyrics_with_llm(lyrics_text: str, api_key: str) -> dict:
    """
    Use OpenAI to validate lyrics format and provide suggestions.

    Returns:
        {
            "valid": bool,
            "issues": list[str],
            "suggestions": list[str],
            "corrected_lyrics": str (optional)
        }
    """
    if not api_key:
        return {"error": "API key required"}

    client = OpenAI(api_key=api_key)

    system_prompt = """You are a Suno AI lyrics format expert. Analyze the provided lyrics for Suno compatibility.

SUNO FORMAT RULES:
1. Use ONLY standard Suno section tags: [Intro], [Verse], [Chorus], [Pre-Chorus], [Bridge], [Outro], [Hook], [Drop], [Breakdown], [Buildup], [Solo], [Instrumental], [Interlude], [Break]
2. Never use custom tags like [Opening Field], [Material Field A], [Movement 1] - Suno won't recognize these as sections
3. A [Style] block at the top is optional but helpful: [Style] (Genre, Key, Tempo)
4. COLON NOTATION is the PREFERRED format for adding instruments/mood to sections:
   - CORRECT: [Intro: ambient pads, soft piano]
   - CORRECT: [Verse: acoustic guitar, mellow tone]
   - CORRECT: [Chorus: full band, high energy]
   This format puts descriptors INSIDE the brackets after a colon. This is VALID - do NOT flag this as an issue.
5. Parenthetical hints (soft piano, building intensity) on separate lines inside sections are ALSO valid
6. Don't have TWO song structures - standard tags + custom tags = confusion

RESPOND WITH JSON ONLY:
{
    "valid": true/false,
    "issues": ["list of issues found"],
    "suggestions": ["list of improvement suggestions"],
    "corrected_lyrics": "corrected version if issues found, otherwise null"
}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze these lyrics for Suno:\n\n{lyrics_text}"},
            ],
            max_tokens=2000,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        return result

    except json.JSONDecodeError:
        return {
            "valid": False,
            "issues": ["Could not parse AI response"],
            "suggestions": [],
            "raw_response": content if 'content' in locals() else "No response",
        }
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Validation error: {str(e)}"],
            "suggestions": [],
        }


# =============================================================================
# SONG TITLE SUGGESTION
# =============================================================================

TITLE_ADJECTIVES = {
    "Mellow": ["Midnight", "Velvet", "Quiet", "Soft", "Dreamy", "Gentle", "Hazy", "Tender"],
    "Intimate": ["Whispered", "Secret", "Hidden", "Private", "Silent", "Close", "Dear"],
    "Uplifting": ["Golden", "Rising", "Shining", "Bright", "Soaring", "Radiant", "Glowing"],
    "Energetic": ["Electric", "Blazing", "Fierce", "Wild", "Burning", "Rushing", "Vivid"],
    "Melancholic": ["Fading", "Lost", "Broken", "Distant", "Longing", "Weeping", "Hollow"],
    "Dreamy": ["Floating", "Drifting", "Ethereal", "Misty", "Hazy", "Wandering", "Starlit"],
    "Dark": ["Shadow", "Obsidian", "Haunted", "Phantom", "Noir", "Midnight", "Ashen"],
    "Searching": ["Cosmic", "Ethereal", "Sacred", "Divine", "Transcendent", "Infinite"],
    "Calm": ["Serene", "Still", "Peaceful", "Gentle", "Quiet", "Restful"],
    "Focused": ["Steady", "Clear", "Sharp", "Precise", "Direct", "Unwavering"],
    "Relaxed": ["Lazy", "Easy", "Warm", "Sunlit", "Breezy", "Mellow"],
    "Creative": ["Vivid", "Curious", "Open", "Bright", "Fresh", "Sparking"],
    "default": ["Midnight", "Golden", "Silver", "Velvet", "Crystal"],
}

TITLE_NOUNS = {
    "Jazz": ["Groove", "Swing", "Rhythm", "Blues", "Serenade", "Quartet", "Nocturne", "Ballad"],
    "Rock": ["Thunder", "Storm", "Fire", "Edge", "Revolt", "Anthem", "Riff", "Scream"],
    "Pop": ["Dreams", "Hearts", "Stars", "Love", "Lights", "Dance", "Summer", "Night"],
    "Hip-Hop": ["Streets", "Crown", "Legacy", "Wave", "Flow", "Empire", "Kingdom"],
    "Electronic": ["Pulse", "Signal", "Circuit", "Wave", "Binary", "Neon", "Grid"],
    "EDM": ["Drop", "Rave", "Pulse", "Energy", "Festival", "Peak", "Release"],
    "Ambient": ["Horizons", "Echoes", "Waves", "Drift", "Stillness", "Clouds", "Mist"],
    "Metal": ["Wrath", "Fury", "Doom", "Abyss", "Chaos", "Reign", "Vengeance"],
    "Lo-fi": ["Memories", "Rain", "Coffee", "Sunset", "Window", "Pages", "Dust"],
    "Classical": ["Opus", "Symphony", "Movement", "Prelude", "Sonata", "Aria"],
    "Meditation": ["Breath", "Stillness", "Serenity", "Silence", "Peace", "Harmony"],
    "Synthwave": ["Neon", "Grid", "Drive", "Horizon", "Chrome", "Vapor"],
    "Techno": ["Pulse", "Sequence", "Pattern", "Grid", "Signal", "Loop"],
    "default": ["Song", "Track", "Piece", "Journey", "Story", "Moment"],
}

TITLE_SUFFIXES = {
    "Dorian": ["Dreams", "Shadows", "Tales", "Echoes"],
    "Phrygian": ["Descent", "Fury", "Storm", "Depths"],
    "Lydian": ["Ascent", "Heights", "Flight", "Wonder"],
    "Mixolydian": ["Groove", "Shuffle", "Road", "Blues"],
    "Aeolian (Minor)": ["Lament", "Sorrow", "Tears", "Night"],
    "Locrian": ["Void", "Fracture", "Collapse", "Dissonance"],
    "default": [],
}


def suggest_song_title(
    genre: str,
    mood: str,
    key: str,
    mode: str,
    use_llm: bool = False,
    api_key: str = None,
    style_preset: str = "",
    tempo: str = "",
    tech_context: str = "",
    profile: str = "General Purpose",
    sections: list = None,
) -> str:
    """
    Generate a suggested song title based on music settings.

    Returns:
        Suggested song title string.
    """
    context = {
        "genre": genre,
        "mood": mood,
        "key": key,
        "mode": mode,
        "style_preset": style_preset,
        "tempo": tempo,
        "tech_context": tech_context,
        "profile": profile,
        "sections": sections or [],
    }
    if use_llm and api_key:
        return _suggest_title_with_llm(api_key=api_key, **context)
    return _suggest_title_local(**context)


def _suggest_title_local(
    genre: str,
    mood: str,
    key: str,
    mode: str,
    style_preset: str = "",
    tempo: str = "",
    tech_context: str = "",
    profile: str = "General Purpose",
    sections: list = None,
) -> str:
    """Local algorithm for title generation using word banks."""
    # Developer Focus: tech-flavored titles
    if profile == "Developer Focus" and style_preset and style_preset != "None":
        dev_prefixes = [
            "Flow State", "Deep Focus", "Code Session", "Debug Mode",
            "Build Loop", "Compile Time", "Neural Path", "Stack Trace",
        ]
        dev_suffixes = [
            "Protocol", "Sequence", "Routine", "Process",
            "Thread", "Session", "Signal", "Cycle",
        ]
        prefix = random.choice(dev_prefixes)
        if tech_context:
            context_short = " ".join(tech_context.split()[:3]).rstrip(",.")
            return f"{prefix} — {context_short}"
        return f"{prefix} {random.choice(dev_suffixes)}"

    # Get adjective based on mood
    adj_list = TITLE_ADJECTIVES.get(mood, TITLE_ADJECTIVES["default"])
    adj = random.choice(adj_list)

    # Get noun based on genre
    noun_list = TITLE_NOUNS.get(genre, TITLE_NOUNS["default"])
    noun = random.choice(noun_list)

    # Sometimes add mode-based suffix
    mode_key = mode.split(" (")[0] if " (" in mode else mode
    suffix_list = TITLE_SUFFIXES.get(mode, TITLE_SUFFIXES.get(mode_key, []))

    # Build title with variety
    pattern = random.choice(["adj_noun", "adj_mode_noun", "noun_in_key", "simple"])

    if pattern == "adj_noun":
        return f"{adj} {noun}"
    elif pattern == "adj_mode_noun" and suffix_list:
        suffix = random.choice(suffix_list)
        return f"{adj} {suffix}"
    elif pattern == "noun_in_key" and key and key != "None":
        key_note = key.split(" ")[0]
        return f"{noun} in {key_note}"
    else:
        return f"{adj} {noun}"


def _suggest_title_with_llm(
    genre: str,
    mood: str,
    key: str,
    mode: str,
    api_key: str,
    style_preset: str = "",
    tempo: str = "",
    tech_context: str = "",
    profile: str = "General Purpose",
    sections: list = None,
) -> str:
    """AI-powered title suggestion using OpenAI."""
    client = OpenAI(api_key=api_key)

    chars = [
        f"- Genre: {genre}",
        f"- Mood: {mood if mood != 'None' else 'neutral'}",
    ]
    if key and key != "None":
        chars.append(f"- Key: {key}")
    if mode and mode != "Ionian (Major)":
        chars.append(f"- Mode: {mode}")
    if style_preset and style_preset != "None":
        chars.append(f"- Style preset: {style_preset}")
    if tempo and tempo != "None":
        chars.append(f"- Tempo: {tempo}")

    if sections:
        section_types = [s.get("type", "") for s in sections if s.get("type")]
        if section_types:
            chars.append(f"- Song arc: {' -> '.join(section_types)}")

    if profile == "Developer Focus":
        chars.append("- Purpose: Background music for software development/coding")
        if tech_context:
            chars.append(f"- Developer context: {tech_context}")

    characteristics = "\n".join(chars)

    prompt = f"""Generate a creative, evocative song title for a track with these characteristics:
{characteristics}

Requirements:
- Title should be 2-5 words maximum
- Should evoke the mood, style and purpose of the track
- Should be memorable and unique
- No quotes around the title
- Just return the title, nothing else"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.9,
        )
        title = response.choices[0].message.content.strip()
        title = title.strip('"\'')
        return title
    except Exception:
        return _suggest_title_local(
            genre, mood, key, mode,
            style_preset=style_preset, tempo=tempo,
            tech_context=tech_context, profile=profile, sections=sections,
        )


# =============================================================================
# SECTION INSTRUMENTS SUGGESTION
# =============================================================================

def suggest_section_instruments(
    sections: list,
    genre: str,
    mood: str,
    key: str = None,
    mode: str = None,
    tempo: str = None,
    time_sig: str = None,
    style_preset: str = None,
    style_influence: str = None,
    progression: str = None,
    api_key: str = None,
) -> list:
    """
    Suggest instruments for each section based on current music settings.

    Returns:
        List of sections with filled instruments fields.
    """
    if api_key:
        return _suggest_sections_with_llm(
            sections, genre, mood, key, mode, tempo, time_sig,
            style_preset, style_influence, progression, api_key,
        )
    return _suggest_sections_local(sections, genre, mood)


def _suggest_sections_local(sections: list, genre: str, mood: str) -> list:
    """Fill sections using local mapping, with mood-awareness."""
    filled = []
    for section in sections:
        new_section = section.copy()
        if not section.get("instruments"):
            new_section["instruments"] = _get_mood_appropriate_instruments(
                section["type"], genre,
                mood if mood and mood != "None" else "default",
            )
        filled.append(new_section)
    return filled


def _suggest_sections_with_llm(
    sections: list,
    genre: str,
    mood: str,
    key: str,
    mode: str,
    tempo: str,
    time_sig: str,
    style_preset: str,
    style_influence: str,
    progression: str,
    api_key: str,
) -> list:
    """Fill sections using AI based on all music settings."""
    client = OpenAI(api_key=api_key)

    context_parts = [f"Genre: {genre}"]
    if mood and mood != "None":
        context_parts.append(f"Mood: {mood}")
    if key and key != "None":
        context_parts.append(f"Key: {key}")
    if mode and mode != "Ionian (Major)":
        context_parts.append(f"Mode: {mode}")
    if tempo and tempo != "None":
        context_parts.append(f"Tempo: {tempo}")
    if time_sig and time_sig != "4/4":
        context_parts.append(f"Time Signature: {time_sig}")
    if style_preset and style_preset != "None":
        context_parts.append(f"Style: {style_preset}")
    if style_influence and style_influence != "None":
        context_parts.append(f"Influence: {style_influence}")
    if progression and progression != "None":
        context_parts.append(f"Chord Progression: {progression}")

    context = "\n".join(context_parts)
    section_list = [s["type"] for s in sections]

    prompt = f"""For a song with these characteristics:
{context}

Suggest appropriate instruments/descriptors for each section (short, comma-separated phrases):
{chr(10).join(f"- {s}" for s in section_list)}

Requirements:
- Each suggestion should be 5-15 words
- Focus on instruments, textures, energy level, playing style
- Match the genre and mood
- For {genre} genre, use typical instruments

Respond in this exact format (one line per section):
{chr(10).join(f"{s}: <your suggestion>" for s in section_list)}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()

        suggestions = {}
        for line in content.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                section_type = parts[0].strip()
                instruments = parts[1].strip()
                suggestions[section_type] = instruments

        filled = []
        for section in sections:
            new_section = section.copy()
            if not section.get("instruments"):
                section_type = section["type"]
                if section_type in suggestions:
                    new_section["instruments"] = suggestions[section_type]
            filled.append(new_section)

        return filled

    except Exception:
        return _suggest_sections_local(sections, genre, mood)


def _get_mood_appropriate_instruments(
    section_type: str, genre: str, mood: str
) -> str:
    """
    Get mood-appropriate instruments for a section.

    Handles calm moods specially to avoid high-energy terms,
    then falls back to data.py section instruments.
    """
    calm_moods = ["Intimate", "Mellow", "Contemplative", "Serene"]

    if mood in calm_moods:
        calm_instruments = {
            "Intro": {
                "Intimate": "soft ambient pads, gentle piano, whispered textures",
                "Mellow": "warm pads, soft keys, gentle atmosphere",
                "Contemplative": "spacious piano, minimal texture, reflective",
                "Serene": "ethereal pads, distant chimes, peaceful tones",
            },
            "Verse": {
                "Intimate": "delicate acoustic guitar, soft voice, gentle dynamics",
                "Mellow": "warm guitar, soft accompaniment, relaxed feel",
                "Contemplative": "thoughtful melody, minimal backing, space",
                "Serene": "flowing melody, gentle strings, calm progression",
            },
            "Chorus": {
                "Intimate": "layered harmonies, soft dynamics, emotional peak",
                "Mellow": "warm build, gentle crescendo, soft fullness",
                "Contemplative": "expanded texture, still restrained, meaningful",
                "Serene": "flowing harmonies, gentle swells, peaceful climax",
            },
            "Buildup": {
                "Intimate": "complex rhythmic textures, driving bass pulse, layered atmosphere",
                "Mellow": "gentle momentum, layered arpeggios, warm bass pulse",
                "Contemplative": "rising harmonic tension, expanding textures, purposeful motion",
                "Serene": "swelling pads, rhythmic pulse, transcendent building",
            },
            "Bridge": {
                "Intimate": "stripped back, vulnerable, single instrument",
                "Mellow": "different texture, still relaxed, contrast",
                "Contemplative": "deeper reflection, minimal, searching",
                "Serene": "transition, flowing, gentle shift",
            },
            "Outro": {
                "Intimate": "fading softly, final whisper, gentle close",
                "Mellow": "warm fade, gentle resolution, peaceful end",
                "Contemplative": "dissolving, unresolved, open ending",
                "Serene": "peaceful fade, serene close, tranquil finish",
            },
        }

        section_map = calm_instruments.get(section_type, {})
        if mood in section_map:
            return section_map[mood]

    # Fall back to data.py
    from data import get_section_instruments
    return get_section_instruments(
        genre, section_type, mood if mood and mood != "None" else "default"
    )


# =============================================================================
# SECTION CONFLICT DETECTION
# =============================================================================

MOOD_CONFLICT_TERMS = {
    "Intimate": {
        "conflicts": [
            "high energy", "full band", "powerful", "aggressive", "massive",
            "heavy", "loud", "explosive", "intense drums", "wall of sound",
            "shredding",
        ],
        "suggest": "layered textures, gentle dynamics, soft pulse, intimate atmosphere",
    },
    "Mellow": {
        "conflicts": [
            "high energy", "aggressive", "powerful", "heavy", "loud",
            "explosive", "driving", "intense", "massive", "shredding",
            "full band",
        ],
        "suggest": "warm textures, relaxed groove, gentle rhythm, soft layers",
    },
    "Contemplative": {
        "conflicts": [
            "high energy", "aggressive", "explosive", "loud", "heavy",
            "massive", "full band", "driving", "intense",
        ],
        "suggest": "spacious atmosphere, thoughtful progression, minimal texture, reflective",
    },
    "Serene": {
        "conflicts": [
            "high energy", "aggressive", "heavy", "loud", "explosive",
            "intense", "driving", "massive", "full band", "powerful drums",
        ],
        "suggest": "flowing textures, gentle pulse, ambient layers, peaceful atmosphere",
    },
    "Dark": {
        "conflicts": ["bright", "happy", "cheerful", "uplifting", "sunny"],
        "suggest": "shadowy textures, minor harmonies, brooding atmosphere, mysterious",
    },
    "Energetic": {
        "conflicts": [
            "mellow", "soft", "quiet", "gentle", "fading", "ambient pads",
            "minimal",
        ],
        "suggest": "driving rhythm, dynamic textures, powerful momentum, building energy",
    },
}

GENRE_CONFLICT_TERMS = {
    "Meditation": {
        "conflicts": [
            "full band", "high energy", "aggressive", "loud", "heavy drums",
            "electric guitar", "distortion", "powerful",
        ],
        "suggest": "ambient pads, soft tones, gentle, peaceful, minimal",
    },
    "Ambient": {
        "conflicts": [
            "full band", "high energy", "aggressive", "drums", "heavy",
            "loud", "distortion",
        ],
        "suggest": "atmospheric, pads, textures, spacious, minimal",
    },
    "Classical": {
        "conflicts": ["synth", "808s", "beats", "electronic", "distortion", "wah"],
        "suggest": "orchestral, strings, dynamics, acoustic",
    },
    "Lo-fi": {
        "conflicts": [
            "aggressive", "loud", "heavy", "distortion", "shredding", "powerful",
        ],
        "suggest": "warm, dusty, mellow, vinyl, tape",
    },
    "Metal": {
        "conflicts": [
            "soft", "gentle", "ambient pads", "peaceful", "mellow", "quiet",
        ],
        "suggest": "heavy, aggressive, distorted, powerful, intense",
    },
    "EDM": {
        "conflicts": ["acoustic guitar", "orchestral", "strings", "piano ballad"],
        "suggest": "synths, drops, builds, electronic beats",
    },
}


def detect_section_conflicts(
    sections: list,
    genre: str,
    mood: str,
) -> list:
    """
    Detect conflicts between section instruments and the selected mood/genre.

    Returns:
        List of warning dicts: {"section", "conflict", "suggestion", "type"}
    """
    warnings = []

    mood_conflicts = MOOD_CONFLICT_TERMS.get(mood, {})
    genre_conflicts = GENRE_CONFLICT_TERMS.get(genre, {})

    for section in sections:
        section_type = section.get("type", "")
        instruments = section.get("instruments", "").lower()

        if not instruments:
            continue

        # Check mood conflicts
        if mood_conflicts:
            for conflict_term in mood_conflicts.get("conflicts", []):
                if conflict_term.lower() in instruments:
                    warnings.append({
                        "section": section_type,
                        "conflict": f'"{conflict_term}" conflicts with {mood} mood',
                        "suggestion": mood_conflicts.get("suggest", ""),
                        "type": "mood",
                    })
                    break

        # Check genre conflicts
        if genre_conflicts:
            for conflict_term in genre_conflicts.get("conflicts", []):
                if conflict_term.lower() in instruments:
                    already_warned = any(
                        w["section"] == section_type for w in warnings
                    )
                    if not already_warned:
                        warnings.append({
                            "section": section_type,
                            "conflict": f'"{conflict_term}" conflicts with {genre} genre',
                            "suggestion": genre_conflicts.get("suggest", ""),
                            "type": "genre",
                        })
                        break

    # Structural checks
    types = [s.get("type") for s in sections]
    if not any(t in types for t in ["Intro", "Opening"]):
        warnings.append({
            "section": "(structure)",
            "conflict": "No intro section",
            "suggestion": "Consider adding an Intro section for a smoother start.",
            "type": "structure",
        })
    if not any(t in types for t in ["Outro", "Ending", "Coda"]):
        warnings.append({
            "section": "(structure)",
            "conflict": "No outro section",
            "suggestion": "Consider adding an Outro section for a clean ending.",
            "type": "structure",
        })

    return warnings


# =============================================================================
# META TAG BUILDER
# =============================================================================

def build_meta_tag(section_type: str, instruments: str = "") -> str:
    """Build a single meta tag string."""
    if instruments:
        return f"[{section_type}: {instruments}]"
    return f"[{section_type}]"
