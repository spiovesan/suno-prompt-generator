"""
LLM-powered prompt generator that creates coherent Suno prompts.
"""

import os
import json
import hashlib
from openai import OpenAI
from prompt_cache import get_cached, set_cached

SYSTEM_PROMPT = """You are a Suno AI music prompt specialist. Generate a coherent,
well-crafted music prompt that combines all the user's selections harmoniously.

## HARD CONSTRAINTS (NEVER VIOLATE):
- QUARTET ONLY: guitar, piano, bass, drums - NO saxophone, brass, strings, vocals, or other instruments
- GUITAR IS LEAD: Guitar plays melody/theme, piano provides harmonic support only
- NO NEGATIVE TERMS: Never use "no", "without", "don't" - Suno ignores negatives
- NO ARTIST NAMES: Never use musician names (no Coltrane, Metheny, Scofield, etc.) - Suno blocks these
- UNDER 200 WORDS: Keep prompts concise
- COMMA-SEPARATED: Use comma-separated descriptors

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


def generate_prompt(selections: dict, api_key: str = None) -> dict:
    """
    Generate a coherent prompt using LLM.

    Returns: {"prompt": str, "cached": bool}
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key required")

    # Create cache key from selections
    cache_key = hashlib.md5(json.dumps(selections, sort_keys=True).encode()).hexdigest()

    # Check cache
    cached = get_cached(cache_key)
    if cached:
        return {"prompt": cached, "cached": True}

    # Build user message from selections
    user_msg = build_selection_message(selections)

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=500,
        temperature=0.7
    )

    prompt = response.choices[0].message.content.strip()

    # Cache result
    set_cached(cache_key, prompt)

    return {"prompt": prompt, "cached": False}


def build_selection_message(selections: dict) -> str:
    """Build the user message from selections."""
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

    if selections.get("intro") and selections["intro"] != "None":
        parts.append(f"Intro: {selections['intro']}")

    # Harmony parameters - pass through bracket tags directly
    if selections.get("progression") and selections["progression"] != "None":
        parts.append(f"Chord Progression: {selections['progression']}")

    if selections.get("harmonic_rhythm") and selections["harmonic_rhythm"] != "None":
        parts.append(f"Harmonic Rhythm: {selections['harmonic_rhythm']}")

    if selections.get("extensions") and selections["extensions"] != "None":
        parts.append(f"Chord Extensions: {selections['extensions']}")

    if not parts:
        return "Generate a default smooth jazz quartet prompt with guitar lead and [complex chord progression]"

    return "Generate a Suno prompt for:\n" + "\n".join(parts)
