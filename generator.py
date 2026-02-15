"""
Unified generator for Suno Prompt Studio.
Handles both Jazz mode (presets + LLM) and Universal mode (audio quality template).
"""

import os
import re
import json
import random
import hashlib
from openai import OpenAI
from cache import get_cached, set_cached
from data import (
    STYLE_PRESETS, STYLE_INFLUENCES, AUDIO_QUALITY_TEMPLATE,
    resolve_preset_value, resolve_influence_value,
    GUITAR_REPLACE_REMOVE, GUITAR_REPLACE_APPEND, LYRIC_TEMPLATES
)


# =============================================================================
# LLM SYSTEM PROMPT (Jazz Mode)
# =============================================================================

JAZZ_SYSTEM_PROMPT = """You are a Suno AI music prompt specialist. Generate a coherent,
well-crafted music prompt that combines all the user's selections harmoniously.

## HARD CONSTRAINTS (NEVER VIOLATE):
- QUARTET ONLY: guitar, piano, bass, drums - NO saxophone, brass, strings, vocals, or other instruments
- GUITAR IS LEAD: Guitar plays melody/theme, piano provides harmonic support only
- NO NEGATIVE TERMS: Never use "no", "without", "don't" - Suno ignores negatives
- NO ARTIST NAMES: Never use musician names (no Coltrane, Metheny, Scofield, etc.) - Suno blocks these
- UNDER 200 WORDS: Keep prompts concise
- COMMA-SEPARATED: Use comma-separated descriptors
- LYRICS FIELD IS SEPARATE: If a lyric template is mentioned, it informs the aesthetic but do NOT include lyrics content in the style prompt
- GUITAR REPLACEMENT MODE: When the user indicates they will replace the guitar stem, ensure guitar is ALWAYS the primary melodic voice. Piano, bass, drums provide ONLY harmonic and rhythmic support. Never use "fusion", "lead piano", "expressive soloist", "piano solo", or "keyboard solo"

## COHERENCE RULES:
- If mood is "Intimate" or "Mellow", use clean guitar tones, brushed drums, soft dynamics
- If mood is "Energetic" or "Dark", allow more aggressive tones but still respect tempo
- Slow tempos (60-80 BPM) should have spacious arrangements, not "powerful" or "funky"
- Fast tempos allow driving energy and complex passages
- Spiritual/Searching moods need contemplative, building arrangements

## HARMONY RULES (CRITICAL - avoid boring progressions):
- NEVER use simple IVm7-Im7 or VIm7-IVmaj7 loops - these are BORING
- Include bracket tags for chord control when harmony params specified
- When progression type is specified, INCLUDE IT AS A BRACKET TAG in output
- Suno understands: [ii-V-I progression], [tritone substitutions], [modal vamp], [complex chord progression]
- For extended chords, use: [9th chords], [altered dominants], [quartal voicings]
- Match harmonic rhythm to tempo (fast tempo = can handle fast changes)
- If no progression specified, default to [complex chord progression, jazz influences]

## STYLE KNOWLEDGE:
- Smooth Jazz: warm hollow-body guitar, Rhodes piano, groovy bass, brushed drums
- Bebop: virtuosic guitar runs, comping piano, walking bass, crisp drums
- Modal Jazz: expressive guitar with sustain, piano pads, pedal bass
- Jazz Fusion: can be aggressive but adapt to mood - clean tones for mellow, distorted for energetic
- Latin Jazz: nylon guitar, montuno piano patterns, syncopated rhythms
- Cool Jazz: mellow guitar, relaxed feel, understated bass
- Hard Bop: bluesy guitar, soulful piano, gospel influences
- Post-Bop: angular guitar lines, chromatic runs, polyrhythmic drums
- Acid Jazz: funky guitar riffs, organ/Rhodes, breakbeat elements
- ECM Style: ambient guitar with reverb, spacious piano, minimalist

## OUTPUT FORMAT:
Return ONLY the prompt text, no explanations or formatting. Use comma-separated descriptors."""


# =============================================================================
# GENERATION FUNCTIONS
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
    lyric_template: str = "",
    # Jazz-specific
    style_preset: str = "",
    style_influence: str = "",
    progression: str = "",
    harmonic_rhythm: str = "",
    extensions: str = "",
    # Options
    replace_guitar: bool = False,
    use_llm: bool = False,
    api_key: str = None
) -> dict:
    """
    Generate Style and Lyrics outputs for Suno.

    For Jazz genre: Uses style presets and optionally LLM for style field.
    For other genres: Uses audio quality template for style field.

    Args:
        genre: Selected genre (Jazz, Pop, Rock, etc.)
        key: Key signature (C Major, A Minor, etc.)
        mode: Musical mode (Dorian, Mixolydian, etc.)
        tempo: Tempo range description
        time_sig: Time signature (4/4, 3/4, etc.)
        mood: Mood description
        sections: List of section dicts with keys: type, instruments
        suno_lyrics: Pasted lyrics from Suno (takes precedence)
        lyric_template: Selected lyric template name
        style_preset: Jazz style preset name
        style_influence: Jazz style influence name
        progression: Chord progression bracket tag
        harmonic_rhythm: Harmonic rhythm bracket tag
        extensions: Chord extensions bracket tag
        replace_guitar: If True, enforce guitar as lead
        use_llm: If True, use LLM for Jazz style generation
        api_key: OpenAI API key (required for LLM mode)

    Returns:
        {"style": str, "lyrics": str, "cached": bool}
    """
    sections = sections or []
    cached = False

    # Extract section-based style hints to reinforce in Style field
    section_style_hints = _extract_section_style_hints(sections)

    # Build STYLE output
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
                api_key=api_key
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
                replace_guitar=replace_guitar
            )
            # Append section hints for static mode
            if section_style_hints:
                style_output += ", " + section_style_hints
    else:
        # Universal mode - use audio quality template + music foundation hints
        style_output = AUDIO_QUALITY_TEMPLATE.format(genre=genre)

        # Build music foundation hints from selections
        music_hints = _build_music_foundation_hints(
            key=key,
            mode=mode,
            tempo=tempo,
            mood=mood,
            time_sig=time_sig
        )
        if music_hints:
            style_output += ", " + music_hints

        # Add harmony options (these work for all genres)
        harmony_additions = [progression, harmonic_rhythm, extensions]
        harmony_additions = [h for h in harmony_additions if h and h != "None" and h.strip()]
        if harmony_additions:
            style_output += ", " + ", ".join(harmony_additions)

        # Add style influence if set (using resolved value for genre)
        if style_influence and style_influence != "None":
            influence_value = resolve_influence_value(style_influence, genre)
            if influence_value:
                style_output += ", " + influence_value

        # Append section-based style hints
        if section_style_hints:
            style_output += ", " + section_style_hints

    # Build LYRICS output
    lyrics_output = _build_lyrics_output(
        genre=genre,
        key=key,
        mode=mode,
        tempo=tempo,
        time_sig=time_sig,
        sections=sections,
        suno_lyrics=suno_lyrics,
        lyric_template=lyric_template
    )

    # Truncate style output to stay under 1000 characters
    MAX_STYLE_LENGTH = 1000
    if len(style_output) > MAX_STYLE_LENGTH:
        # Try to truncate at a comma boundary for cleaner output
        truncated = style_output[:MAX_STYLE_LENGTH]
        last_comma = truncated.rfind(", ")
        if last_comma > MAX_STYLE_LENGTH // 2:  # Only if comma is in second half
            style_output = truncated[:last_comma]
        else:
            style_output = truncated.rstrip(", ")

    return {
        "style": style_output,
        "lyrics": lyrics_output,
        "cached": cached
    }


def _generate_jazz_static(
    style_preset: str,
    key: str,
    style_influence: str,
    tempo: str,
    mood: str,
    progression: str,
    harmonic_rhythm: str,
    extensions: str,
    replace_guitar: bool
) -> str:
    """Generate jazz prompt using static concatenation."""
    # Use style preset as base
    base = STYLE_PRESETS.get(style_preset, STYLE_PRESETS["Smooth Jazz"])

    # Get style influence value
    influence_value = STYLE_INFLUENCES.get(style_influence, "")

    # Build additions
    additions = [key, influence_value, tempo, mood, progression, harmonic_rhythm, extensions]
    additions = [a for a in additions if a and a != "None"]

    result = base + (", " + ", ".join(additions) if additions else "")

    # Apply guitar replacement if needed
    if replace_guitar:
        result = _apply_guitar_replacement(result)

    return result


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
    api_key: str
) -> dict:
    """Generate jazz prompt using LLM."""
    # Extract section hints for LLM context
    section_hints = _extract_section_style_hints(sections)

    # Build selections dict for cache key
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
        "section_hints": section_hints
    }

    # Create cache key
    cache_key = hashlib.md5(json.dumps(selections, sort_keys=True).encode()).hexdigest()

    # Check cache
    cached = get_cached(cache_key)
    if cached:
        return {"prompt": cached, "cached": True}

    # Build user message
    user_msg = _build_llm_message(selections)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JAZZ_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=500,
        temperature=0.7
    )

    prompt = response.choices[0].message.content.strip()

    # Cache result
    set_cached(cache_key, prompt)

    return {"prompt": prompt, "cached": False}


def _build_llm_message(selections: dict) -> str:
    """Build the user message for LLM from selections."""
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
        parts.append(f"Aesthetic context: {selections['lyric_template']} (do NOT include lyrics in output)")

    if selections.get("replace_guitar"):
        parts.append("IMPORTANT: User will replace the guitar stem. Guitar MUST be the only melodic voice. "
                     "Piano/bass/drums provide only support. Avoid: fusion, lead piano, expressive soloist.")

    if selections.get("section_hints"):
        parts.append(f"Song features: {selections['section_hints']} (include these characteristics in prompt)")

    if not parts:
        return "Generate a default smooth jazz quartet prompt with guitar lead and [complex chord progression]"

    return "Generate a Suno prompt for:\n" + "\n".join(parts)


def _apply_guitar_replacement(prompt: str) -> str:
    """Apply guitar replacement filtering to a prompt."""
    result = prompt
    for term in GUITAR_REPLACE_REMOVE:
        result = re.sub(re.escape(term), "", result, flags=re.IGNORECASE)
    # Clean up double commas/spaces
    result = re.sub(r",\s*,", ",", result)
    result = re.sub(r"\s{2,}", " ", result)
    result = result.strip(", ")
    result += ", " + GUITAR_REPLACE_APPEND
    return result


def _build_music_foundation_hints(
    key: str = "",
    mode: str = "",
    tempo: str = "",
    mood: str = "",
    time_sig: str = ""
) -> str:
    """
    Build music foundation hints from user selections for the Style field.

    This ensures the Style output changes when users modify key, mode, tempo,
    mood, or time signature selections.

    Returns comma-separated hints string.
    """
    hints = []

    # Add key signature
    if key and key != "None":
        hints.append(f"in {key}")

    # Add mode (extract just the name without parenthetical)
    if mode and mode != "Ionian (Major)" and mode != "None":
        mode_name = mode.split(" (")[0] if " (" in mode else mode
        hints.append(f"{mode_name} mode")

    # Add tempo
    if tempo and tempo != "None":
        hints.append(f"{tempo} tempo")

    # Add mood
    if mood and mood != "None":
        hints.append(f"{mood} mood")

    # Add time signature if unusual
    if time_sig and time_sig != "4/4" and time_sig != "None":
        hints.append(f"{time_sig} time signature")

    return ", ".join(hints) if hints else ""


def _extract_section_style_hints(sections: list) -> str:
    """
    Extract style hints from sections to reinforce in the Style field.

    This helps Suno better understand and execute special sections like
    Solo, Instrumental, Break, etc. since it reads Style field more reliably.

    Returns comma-separated style hints string.
    """
    if not sections:
        return ""

    hints = []

    # Section type to style hint mapping
    section_hints = {
        "instrumental": "instrumental section",
        "break": "breakdown section",
        "drop": "bass drop",
        "build": "building intensity",
        "hook": "catchy hook",
    }

    # Style keywords that indicate a genre/style change within the song
    style_keywords = [
        "metal", "rock", "jazz", "blues", "funk", "classical", "electronic",
        "acoustic", "distorted", "shred", "melodic", "aggressive", "heavy",
        "soft", "ambient", "intense", "epic", "dramatic"
    ]

    # Track which hints we've added to avoid duplicates
    added_hints = set()

    for section in sections:
        section_type = section.get("type", "").lower()
        instruments = section.get("instruments", "").lower()

        # Check for solo sections - extract style descriptors
        if section_type == "solo":
            if instruments:
                # Check if instruments field contains style keywords
                found_styles = [kw for kw in style_keywords if kw in instruments]
                if found_styles:
                    # Build a style-focused hint for contrasting solo
                    hint = f"contrasting {instruments} section"
                    if hint not in added_hints:
                        hints.append(hint)
                        added_hints.add(hint)
                else:
                    # Generic solo with instruments
                    hint = f"featuring {instruments} solo" if "solo" not in instruments else f"featuring {instruments}"
                    if hint not in added_hints:
                        hints.append(hint)
                        added_hints.add(hint)
            elif "solo" not in added_hints:
                hints.append("featuring instrumental solo")
                added_hints.add("solo")

        # Check for other special sections
        elif section_type in section_hints:
            hint = section_hints[section_type]
            if hint not in added_hints:
                hints.append(hint)
                added_hints.add(hint)

        # Check any section's instruments field for style contrasts
        if instruments:
            found_styles = [kw for kw in style_keywords if kw in instruments]
            # If section has strong style keywords, add as style variation
            if found_styles and section_type not in ["verse", "chorus", "intro", "outro"]:
                # For non-standard sections with style keywords
                style_desc = " ".join(found_styles[:2])  # Limit to 2 keywords
                contrast_hint = f"with {style_desc} {section_type} section"
                if contrast_hint not in added_hints:
                    hints.append(contrast_hint)
                    added_hints.add(contrast_hint)

            # Check for solo keywords in any section's instruments
            if "solo" in instruments and "solo" not in added_hints:
                solo_match = re.search(r'([^,]*solo[^,]*)', instruments, re.IGNORECASE)
                if solo_match:
                    hint = f"featuring {solo_match.group(1).strip()}"
                    if hint not in added_hints:
                        hints.append(hint)
                        added_hints.add(hint)

    return ", ".join(hints) if hints else ""


def _get_nearest_section_type(section_type: str, available_types: set) -> str:
    """
    Find nearest matching section type for unmapped lyrics.

    CONSERVATIVE: Only maps true synonyms (hook ↔ chorus, refrain ↔ chorus).
    Sections without direct match or synonym stay INSTRUMENTAL (return None).

    Args:
        section_type: The section type to find a match for (e.g., "bridge")
        available_types: Set of section types available in the lyrics

    Returns:
        The nearest matching section type, or None to stay instrumental
    """
    section_type = section_type.lower()

    # If the type is already available, return it directly
    if section_type in available_types:
        return section_type

    # ONLY true synonyms - these are essentially the same section type
    SYNONYMS = {
        "hook": ["chorus", "refrain"],
        "refrain": ["chorus", "hook"],
        "chorus": ["hook", "refrain"],
    }

    # Only try synonyms - no generic fallbacks
    if section_type in SYNONYMS:
        for synonym in SYNONYMS[section_type]:
            if synonym in available_types:
                return synonym

    # No match found - section stays INSTRUMENTAL (no lyrics)
    return None


def _parse_suno_lyrics(lyrics_text: str) -> dict:
    """
    Parse Suno lyrics to extract sections and their content.

    Returns a dict mapping section types (lowercase) to their lyrics content.
    Example: {"verse": "lyrics here...", "chorus": "chorus lyrics..."}
    """
    if not lyrics_text or not lyrics_text.strip():
        return {}

    sections = {}
    current_section = None
    current_content = []

    # Regex to match section tags like [Verse], [Chorus], [Verse 1], etc.
    section_pattern = re.compile(r'^\[([^\]:]+)(?::[^\]]+)?\]', re.IGNORECASE)

    for line in lyrics_text.strip().split('\n'):
        line_stripped = line.strip()
        match = section_pattern.match(line_stripped)

        if match:
            # Save previous section if any
            if current_section and current_content:
                # Normalize section name (remove numbers, lowercase)
                section_key = re.sub(r'\s*\d+$', '', current_section).lower().strip()
                if section_key not in sections:
                    sections[section_key] = []
                sections[section_key].append('\n'.join(current_content).strip())

            # Start new section
            current_section = match.group(1).strip()
            current_content = []
        elif current_section:
            # Add line to current section (preserve non-empty lines)
            if line_stripped or current_content:  # Keep empty lines within content
                current_content.append(line)

    # Save last section
    if current_section and current_content:
        section_key = re.sub(r'\s*\d+$', '', current_section).lower().strip()
        if section_key not in sections:
            sections[section_key] = []
        sections[section_key].append('\n'.join(current_content).strip())

    return sections


def parse_lyrics_to_sections(lyrics_text: str) -> list:
    """
    Parse pasted Suno lyrics and return section list for Song Structure.

    This function extracts section tags from pasted lyrics and returns them
    in a format suitable for the Song Structure editor.

    Args:
        lyrics_text: Raw pasted lyrics with [SectionType] tags

    Returns:
        List of section dicts: [{"id": "...", "type": "Verse", "instruments": ""}, ...]
    """
    if not lyrics_text or not lyrics_text.strip():
        return []

    import uuid

    sections = []

    # Match section tags like [Verse], [Chorus], [Verse 2], [Solo: guitar]
    tag_pattern = re.compile(r'\[([^\]:]+)(?::\s*([^\]]+))?\]', re.IGNORECASE)

    for match in tag_pattern.finditer(lyrics_text):
        section_type = match.group(1).strip()
        instruments = match.group(2).strip() if match.group(2) else ""

        # Normalize: "Verse 1" -> "Verse", "CHORUS" -> "Chorus"
        normalized_type = re.sub(r'\s*\d+$', '', section_type).strip()
        # Title case: "verse" -> "Verse", "pre-chorus" -> "Pre-Chorus"
        normalized_type = normalized_type.title()

        # Skip non-section tags like [Style], [End]
        if normalized_type.lower() in ['style', 'end']:
            continue

        sections.append({
            "id": str(uuid.uuid4()),
            "type": normalized_type,
            "instruments": instruments
        })

    return sections


def _build_lyrics_output(
    genre: str,
    key: str,
    mode: str,
    tempo: str,
    time_sig: str,
    sections: list,
    suno_lyrics: str,
    lyric_template: str
) -> str:
    """
    Build the Lyrics field output with [Style] block and meta tags.

    If suno_lyrics is provided, merges section meta tags with matching lyrics.
    """
    lines = []

    # Build [Style] block
    style_parts = [genre]
    if key and key != "None":
        style_parts.append(key)
    if mode and mode != "Ionian (Major)" and mode != "None":
        # Extract just the mode name without parenthetical
        mode_name = mode.split(" (")[0] if " (" in mode else mode
        style_parts.append(mode_name)
    if tempo and tempo != "None":
        style_parts.append(tempo)
    if time_sig and time_sig != "4/4" and time_sig != "None":
        style_parts.append(time_sig)

    lines.append(f"[Style] ({', '.join(style_parts)})")
    lines.append("")

    # Parse pasted lyrics if provided
    parsed_lyrics = _parse_suno_lyrics(suno_lyrics) if suno_lyrics else {}

    # Track which parsed sections we've used (for multiple same-type sections)
    section_counters = {}

    # Build section meta tags merged with lyrics
    for section in sections:
        section_type = section.get("type", "Verse")
        instruments = section.get("instruments", "").strip()

        # Build the meta tag with instruments
        if instruments:
            lines.append(f"[{section_type}: {instruments}]")
        else:
            lines.append(f"[{section_type}]")

        # Try to find matching lyrics for this section type
        section_key = section_type.lower()
        if section_key in parsed_lyrics:
            # Direct match - use lyrics for this section type
            counter = section_counters.get(section_key, 0)
            lyrics_list = parsed_lyrics[section_key]

            if counter < len(lyrics_list):
                # Add the lyrics content
                lines.append(lyrics_list[counter])
                section_counters[section_key] = counter + 1
            # If no more lyrics available for this type, section stays instrumental
        elif parsed_lyrics:
            # No direct match - try synonym only (hook ↔ chorus)
            nearest = _get_nearest_section_type(section_key, set(parsed_lyrics.keys()))
            if nearest and nearest in parsed_lyrics:
                # Use lyrics from synonym type
                counter = section_counters.get(nearest, 0)
                lyrics_list = parsed_lyrics[nearest]
                if counter < len(lyrics_list):
                    lines.append(lyrics_list[counter])
                    section_counters[nearest] = counter + 1
                # If no more lyrics available, section stays instrumental
            # If no synonym found, section stays instrumental (no lyrics added)

        lines.append("")  # Empty line between sections

    # If no parsed lyrics but we have a template, append it
    if not parsed_lyrics and lyric_template and lyric_template != "None":
        template_content = LYRIC_TEMPLATES.get(lyric_template, "")
        if template_content:
            lines.append(template_content)

    return "\n".join(lines).strip()


def build_meta_tag(section_type: str, instruments: str = "") -> str:
    """Build a single meta tag string."""
    if instruments:
        return f"[{section_type}: {instruments}]"
    return f"[{section_type}]"


# =============================================================================
# LYRICS VALIDATION
# =============================================================================

# Standard Suno section tags (recognized by Suno)
STANDARD_SUNO_TAGS = {
    "intro", "verse", "chorus", "pre-chorus", "prechorus", "bridge",
    "outro", "hook", "drop", "breakdown", "buildup", "build",
    "solo", "instrumental", "interlude", "break", "refrain",
    "style", "end"
}


def validate_lyrics_format(lyrics_text: str) -> dict:
    """
    Validate lyrics format for Suno compatibility.

    Checks for:
    - Duplicate/overlapping song structures
    - Non-standard section tags
    - Missing [Style] block
    - Empty sections

    Returns:
        {
            "valid": bool,
            "warnings": list[str],
            "suggestions": list[str],
            "tag_analysis": dict
        }
    """
    if not lyrics_text or not lyrics_text.strip():
        return {
            "valid": True,
            "warnings": [],
            "suggestions": ["Add song structure with section tags like [Intro], [Verse], [Chorus]"],
            "tag_analysis": {}
        }

    warnings = []
    suggestions = []

    # Extract all bracket tags
    tag_pattern = re.compile(r'\[([^\]]+)\]', re.IGNORECASE)
    all_tags = tag_pattern.findall(lyrics_text)

    # Analyze tags
    standard_tags = []
    custom_tags = []
    tag_counts = {}

    for tag in all_tags:
        # Extract base tag name (before colon if any)
        base_tag = tag.split(":")[0].strip().lower()
        # Remove numbers from end (e.g., "Verse 1" -> "verse")
        base_tag_normalized = re.sub(r'\s*\d+$', '', base_tag).strip()

        # Count occurrences
        tag_counts[base_tag_normalized] = tag_counts.get(base_tag_normalized, 0) + 1

        if base_tag_normalized in STANDARD_SUNO_TAGS:
            standard_tags.append(tag)
        else:
            custom_tags.append(tag)

    # Check for duplicate structures (multiple different "structure schemes")
    # This happens when user has both standard tags AND custom tags that look like sections
    structure_like_customs = []
    for tag in custom_tags:
        base = tag.split(":")[0].strip().lower()
        # Tags that look like section names (contain "field", "section", "part", etc.)
        if any(kw in base for kw in ["field", "section", "part", "material", "movement"]):
            structure_like_customs.append(tag)

    if standard_tags and structure_like_customs:
        warnings.append(
            f"⚠️ Duplicate song structures detected! You have standard Suno tags "
            f"({len(standard_tags)} tags like [Verse], [Chorus]) AND custom structure tags "
            f"({len(structure_like_customs)} tags like [{structure_like_customs[0]}]). "
            f"This may cause Suno to create two songs in one."
        )
        suggestions.append(
            "Use ONLY standard Suno tags and put descriptive content inside them as parenthetical hints."
        )

    # Check for non-standard tags
    if custom_tags and not structure_like_customs:
        non_standard_list = list(set([t.split(":")[0].strip() for t in custom_tags[:5]]))
        if non_standard_list:
            warnings.append(
                f"⚠️ Non-standard tags detected: [{'], ['.join(non_standard_list)}]. "
                f"Suno may not recognize these as sections."
            )

    # Check for [Style] block
    has_style = any(t.lower().startswith("style") for t in all_tags)
    if not has_style:
        suggestions.append("Consider adding a [Style] block at the top for genre/key/tempo info.")

    # Check for empty sections (tag followed by another tag or end)
    lines = lyrics_text.strip().split('\n')
    for i, line in enumerate(lines):
        if tag_pattern.match(line.strip()):
            # Check if next non-empty line is also a tag
            for j in range(i + 1, min(i + 3, len(lines))):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('('):
                    if tag_pattern.match(next_line):
                        tag_name = tag_pattern.match(line.strip()).group(1)
                        suggestions.append(f"Section [{tag_name}] has no content. Consider adding descriptive hints.")
                    break

    # Check for very long lyrics (may exceed Suno limits)
    if len(lyrics_text) > 3000:
        warnings.append(f"⚠️ Lyrics are {len(lyrics_text)} characters. Suno may truncate very long lyrics.")

    return {
        "valid": len(warnings) == 0,
        "warnings": warnings,
        "suggestions": suggestions,
        "tag_analysis": {
            "total_tags": len(all_tags),
            "standard_tags": len(standard_tags),
            "custom_tags": len(custom_tags),
            "tag_counts": tag_counts
        }
    }


def validate_lyrics_with_llm(lyrics_text: str, api_key: str) -> dict:
    """
    Use OpenAI to validate lyrics format and provide suggestions.

    Returns:
        {
            "valid": bool,
            "issues": list[str],
            "suggestions": list[str],
            "corrected_lyrics": str (optional, if issues found)
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
                {"role": "user", "content": f"Analyze these lyrics for Suno:\n\n{lyrics_text}"}
            ],
            max_tokens=2000,
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        # Try to parse JSON from response
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
            "raw_response": content if 'content' in locals() else "No response"
        }
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Validation error: {str(e)}"],
            "suggestions": []
        }


# =============================================================================
# SONG TITLE SUGGESTION
# =============================================================================

# Word banks for local title generation
TITLE_ADJECTIVES = {
    "Mellow": ["Midnight", "Velvet", "Quiet", "Soft", "Dreamy", "Gentle", "Hazy", "Tender"],
    "Intimate": ["Whispered", "Secret", "Hidden", "Private", "Silent", "Close", "Dear"],
    "Uplifting": ["Golden", "Rising", "Shining", "Bright", "Soaring", "Radiant", "Glowing"],
    "Energetic": ["Electric", "Blazing", "Fierce", "Wild", "Burning", "Rushing", "Vivid"],
    "Melancholic": ["Fading", "Lost", "Broken", "Distant", "Longing", "Weeping", "Hollow"],
    "Dreamy": ["Floating", "Drifting", "Ethereal", "Misty", "Hazy", "Wandering", "Starlit"],
    "Dark": ["Shadow", "Obsidian", "Haunted", "Phantom", "Noir", "Midnight", "Ashen"],
    "Searching": ["Cosmic", "Ethereal", "Sacred", "Divine", "Transcendent", "Infinite"],
    "default": ["Untitled", "New", "Another", "The"],
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
    "default": ["Song", "Track", "Piece", "Journey", "Story", "Moment"],
}

TITLE_SUFFIXES = {
    "Dorian": ["Dreams", "Shadows", "Tales", "Echoes"],
    "Phrygian": ["Descent", "Fury", "Storm", "Depths"],
    "Lydian": ["Ascent", "Heights", "Flight", "Wonder"],
    "Mixolydian": ["Groove", "Shuffle", "Road", "Blues"],
    "Aeolian (Minor)": ["Lament", "Sorrow", "Tears", "Night"],
    "default": [],
}


def suggest_song_title(
    genre: str,
    mood: str,
    key: str,
    mode: str,
    use_llm: bool = False,
    api_key: str = None
) -> str:
    """
    Generate a suggested song title based on music settings.

    Args:
        genre: Selected genre
        mood: Selected mood
        key: Key signature
        mode: Musical mode
        use_llm: Whether to use AI for generation
        api_key: OpenAI API key (required for LLM mode)

    Returns:
        Suggested song title string
    """
    if use_llm and api_key:
        return _suggest_title_with_llm(genre, mood, key, mode, api_key)
    return _suggest_title_local(genre, mood, key, mode)


def _suggest_title_local(genre: str, mood: str, key: str, mode: str) -> str:
    """Local algorithm for title generation using word banks."""
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
        key_note = key.split(" ")[0]  # e.g., "C" from "C Major"
        return f"{noun} in {key_note}"
    else:
        return f"{adj} {noun}"


def _suggest_title_with_llm(
    genre: str,
    mood: str,
    key: str,
    mode: str,
    api_key: str
) -> str:
    """AI-powered title suggestion using OpenAI."""
    client = OpenAI(api_key=api_key)

    prompt = f"""Generate a creative, evocative song title for a track with these characteristics:
- Genre: {genre}
- Mood: {mood if mood != "None" else "neutral"}
- Key: {key if key != "None" else "not specified"}
- Mode: {mode if mode != "Ionian (Major)" else "major"}

Requirements:
- Title should be 2-4 words maximum
- Should evoke the mood and style
- Should be memorable and unique
- No quotes around the title
- Just return the title, nothing else"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.9
        )
        title = response.choices[0].message.content.strip()
        # Clean up any quotes
        title = title.strip('"\'')
        return title
    except Exception:
        # Fall back to local generation
        return _suggest_title_local(genre, mood, key, mode)


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
    api_key: str = None
) -> list:
    """
    Suggest instruments for each section based on current music settings.

    Args:
        sections: List of section dicts with "id", "type", "instruments"
        genre: Selected genre
        mood: Selected mood
        key: Key signature (optional)
        mode: Musical mode (optional)
        tempo: Tempo range (optional)
        time_sig: Time signature (optional)
        style_preset: Jazz style preset (optional)
        style_influence: Jazz style influence (optional)
        progression: Chord progression (optional)
        api_key: OpenAI API key (optional, enables AI suggestions)

    Returns:
        List of sections with filled instruments fields
    """
    if api_key:
        return _suggest_sections_with_llm(
            sections, genre, mood, key, mode, tempo, time_sig,
            style_preset, style_influence, progression, api_key
        )
    return _suggest_sections_local(sections, genre, mood)


def _suggest_sections_local(sections: list, genre: str, mood: str) -> list:
    """Fill sections using local mapping from data.py."""
    from data import get_section_instruments

    filled = []
    for section in sections:
        new_section = section.copy()
        # Only fill if instruments field is empty
        if not section.get("instruments"):
            new_section["instruments"] = get_section_instruments(
                genre, section["type"], mood if mood and mood != "None" else "default"
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
    api_key: str
) -> list:
    """Fill sections using AI based on all music settings."""
    client = OpenAI(api_key=api_key)

    # Build context from all settings
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
        context_parts.append(f"Jazz Style: {style_preset}")
    if style_influence and style_influence != "None":
        context_parts.append(f"Influence: {style_influence}")
    if progression and progression != "None":
        context_parts.append(f"Chord Progression: {progression}")

    context = "\n".join(context_parts)

    # Get section types
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
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        # Parse response - expect "SectionType: instruments" format
        suggestions = {}
        for line in content.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                section_type = parts[0].strip()
                instruments = parts[1].strip()
                suggestions[section_type] = instruments

        # Apply suggestions to sections
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
        # Fall back to local generation
        return _suggest_sections_local(sections, genre, mood)
