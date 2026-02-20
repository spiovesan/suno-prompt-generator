"""
Iterative suggestion-based refinement for Suno Prompt Studio.

Two-phase cycle:
  1. generate_suggestions() — analyze current prompt, return 3-5 actionable suggestions
  2. apply_suggestions() — apply user-selected suggestions, return refined prompt

Designed for iterative use: suggest → pick → apply → suggest again.
"""

import json
import time
from openai import OpenAI
from refiner_tools import (
    analyze_style_output,
    analyze_lyrics_output,
    analyze_jazz_output,
)


# =============================================================================
# SUGGESTION CATEGORIES
# =============================================================================

SUGGESTION_CATEGORIES = [
    "instrumentation",
    "harmony",
    "mood",
    "structure",
    "technical",
]


# =============================================================================
# SYSTEM PROMPTS
# =============================================================================

SUGGEST_SYSTEM_PROMPT = """You are a Suno AI music prompt refinement advisor.
You analyze Style and Lyrics fields and suggest specific, actionable improvements.

Return a JSON object with a "suggestions" key containing an array of 3-5 suggestions.
Each suggestion must have:
- "id": short unique key ("s1", "s2", ...)
- "category": one of "instrumentation", "harmony", "mood", "structure", "technical"
- "title": concise action phrase (5-10 words)
- "description": what this changes and why (1-2 sentences)
- "preview_style": key phrases that would change in the Style field, or "no change"
- "preview_lyrics": key phrases that would change in the Lyrics field, or "no change"

RULES:
- Each suggestion must be independent — applying any subset should work
- Be specific: name exact instruments, chord types, production terms
- Prioritize impactful changes over cosmetic ones
- Suggestions should be diverse across categories when possible
- Only suggest POSITIVE, prescriptive changes — never "remove X" or "no X"
- Return ONLY the JSON object, no markdown formatting"""

SUGGEST_JAZZ_CONSTRAINTS = """
JAZZ HARD CONSTRAINTS (suggestions must respect these):
- Quartet only: guitar, piano, bass, drums
- NO saxophone, brass, strings, vocals
- Guitar MUST be lead (melody/theme)
- Piano only provides harmonic support (comping)
- NO artist names
- NO negative terms ("no", "without", "don't")"""

APPLY_SYSTEM_PROMPT = """You are a Suno AI music prompt specialist.
Apply the user's selected refinements to produce updated Style and Lyrics fields.

RULES:
- Apply ONLY the selected suggestions — do not make other changes
- Preserve ALL elements not affected by the suggestions
- Keep the user's musical choices intact (genre, key, mode, tempo)
- If user provided additional feedback, incorporate it
- Style field must stay under 1000 characters
- Use comma-separated descriptors for Style field
- Use proper [Section: instruments] format for Lyrics field
- Only use POSITIVE, prescriptive descriptors — never "no X" or "without X"

After applying changes, respond with EXACTLY this format:

REFINED STYLE:
[the updated style field text]

REFINED LYRICS:
[the updated lyrics field text]"""

APPLY_JAZZ_CONSTRAINTS = """
JAZZ HARD CONSTRAINTS (NEVER VIOLATE):
- Quartet only: guitar, piano, bass, drums
- NO saxophone, brass, strings, vocals
- Guitar is ALWAYS lead (melody/theme)
- Piano only comps/supports
- NO artist names
- NO negative terms"""


# =============================================================================
# GENERATE SUGGESTIONS
# =============================================================================

def generate_suggestions(
    style_text: str,
    lyrics_text: str,
    api_key: str,
    is_jazz: bool = False,
    genre: str = "",
    mood: str = "",
    profile: str = "General Purpose",
    iteration_history: list = None,
) -> list:
    """
    Analyze current prompt and return 3-5 refinement suggestions.

    Pre-computes analysis locally using refiner_tools, then makes a single
    LLM call for suggestions. Fast — no multi-round tool calling.

    Returns:
        List of suggestion dicts: [{id, category, title, description, preview_style, preview_lyrics}]
    """
    client = OpenAI(api_key=api_key)

    # Pre-compute analysis locally (fast, no LLM)
    style_analysis = analyze_style_output(style_text)
    lyrics_analysis = analyze_lyrics_output(lyrics_text)
    jazz_analysis = analyze_jazz_output(style_text) if is_jazz else None

    # Build analysis context for the LLM
    analysis_block = f"""## PRE-ANALYSIS (automated):
Style: {style_analysis['coverage']} coverage, issues: {style_analysis['issues'] or 'none'}
Lyrics: {lyrics_analysis['section_count']} sections, issues: {lyrics_analysis['issues'] or 'none'}"""

    if jazz_analysis:
        analysis_block += f"""
Jazz: quartet={jazz_analysis['is_quartet']}, issues: {jazz_analysis['issues'] or 'none'}"""

    # Build history context
    history_block = ""
    if iteration_history and len(iteration_history) > 1:
        applied = []
        for v in iteration_history[1:]:
            for s in v.get("suggestions_shown", []):
                if s.get("id") in v.get("suggestions_applied", []):
                    applied.append(f"- {s['title']} ({s['category']})")
        if applied:
            history_block = f"""
## ALREADY APPLIED (do NOT repeat these):
{chr(10).join(applied)}"""

    # Genre/mood context
    context_block = f"Genre: {genre}" if genre else ""
    if mood:
        context_block += f", Mood: {mood}"
    if profile == "Developer Focus":
        context_block += ", Purpose: background music for focus/coding"

    # Jazz constraints
    jazz_block = SUGGEST_JAZZ_CONSTRAINTS if is_jazz else ""

    # Build system prompt
    system = SUGGEST_SYSTEM_PROMPT + jazz_block

    user_message = f"""{analysis_block}
{history_block}

## CONTEXT:
{context_block}

## CURRENT STYLE FIELD:
{style_text}

## CURRENT LYRICS FIELD:
{lyrics_text}

Analyze these outputs and suggest 3-5 specific improvements."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        max_tokens=1200,
    )

    # Parse response
    try:
        data = json.loads(response.choices[0].message.content)
        suggestions = data.get("suggestions", [])
    except (json.JSONDecodeError, AttributeError):
        suggestions = []

    # Validate and normalize
    valid = []
    for i, s in enumerate(suggestions):
        if not isinstance(s, dict):
            continue
        suggestion = {
            "id": s.get("id", f"s{i+1}"),
            "category": s.get("category", "technical"),
            "title": s.get("title", "Improve prompt"),
            "description": s.get("description", ""),
            "preview_style": s.get("preview_style", "no change"),
            "preview_lyrics": s.get("preview_lyrics", "no change"),
        }
        if suggestion["category"] not in SUGGESTION_CATEGORIES:
            suggestion["category"] = "technical"
        valid.append(suggestion)

    return valid[:5]


# =============================================================================
# APPLY SUGGESTIONS
# =============================================================================

def apply_suggestions(
    style_text: str,
    lyrics_text: str,
    selected_suggestions: list,
    user_feedback: str = "",
    api_key: str = "",
    is_jazz: bool = False,
    genre: str = "",
    mood: str = "",
    profile: str = "General Purpose",
) -> dict:
    """
    Apply selected suggestions to produce refined Style and Lyrics.

    Single LLM call with strong constraints to only apply selected changes.

    Returns:
        {"refined_style": str, "refined_lyrics": str}
    """
    client = OpenAI(api_key=api_key)

    # Build suggestions block
    suggestions_text = ""
    for s in selected_suggestions:
        suggestions_text += f"""
### {s['title']} [{s['category']}]
{s['description']}
Style preview: {s.get('preview_style', 'no change')}
Lyrics preview: {s.get('preview_lyrics', 'no change')}
"""

    # Context
    context = f"Genre: {genre}" if genre else ""
    if mood:
        context += f", Mood: {mood}"
    if profile == "Developer Focus":
        context += ", Purpose: background music for focus/coding"

    # Jazz constraints
    jazz_block = APPLY_JAZZ_CONSTRAINTS if is_jazz else ""

    system = APPLY_SYSTEM_PROMPT + jazz_block

    feedback_block = ""
    if user_feedback and user_feedback.strip():
        feedback_block = f"""
## ADDITIONAL USER DIRECTION:
{user_feedback.strip()}"""

    user_message = f"""## CONTEXT:
{context}

## CURRENT STYLE FIELD:
{style_text}

## CURRENT LYRICS FIELD:
{lyrics_text}

## SUGGESTIONS TO APPLY:
{suggestions_text}
{feedback_block}

Apply ONLY the suggestions listed above. Preserve everything else unchanged."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    final_response = response.choices[0].message.content or ""

    # Parse response
    refined_style = style_text
    refined_lyrics = lyrics_text

    if "REFINED STYLE:" in final_response:
        parts = final_response.split("REFINED STYLE:")
        if len(parts) > 1:
            style_part = parts[1]
            if "REFINED LYRICS:" in style_part:
                refined_style = style_part.split("REFINED LYRICS:")[0].strip()
                refined_lyrics = style_part.split("REFINED LYRICS:")[1].strip()
            else:
                refined_style = style_part.strip()

    # Clean markdown formatting
    refined_style = refined_style.strip('`"\' \n')
    refined_lyrics = refined_lyrics.strip('`"\' \n')

    # Truncate style if too long
    if len(refined_style) > 1000:
        truncated = refined_style[:1000]
        last_comma = truncated.rfind(", ")
        if last_comma > 500:
            refined_style = truncated[:last_comma]
        else:
            refined_style = truncated

    return {
        "refined_style": refined_style,
        "refined_lyrics": refined_lyrics,
    }
