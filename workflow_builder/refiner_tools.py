"""
Agent tools for the Suno Workflow Builder Refiner.
These functions analyze and refine both Style (audio quality) and Lyrics (meta tags) outputs.
"""

import json
import re
from workflow_knowledge import (
    get_meta_tag_guidelines,
    get_audio_quality_guidelines
)


def analyze_style_output(style_text: str) -> dict:
    """
    Analyze the Style field (audio quality) output.

    Returns analysis including:
    - Word count
    - Key elements detected (bass, mids, highs, mastering, etc.)
    - Missing elements
    - Potential issues
    """
    lines = [l.strip() for l in style_text.strip().split('\n') if l.strip()]
    word_count = len(style_text.split())

    # Key elements to check for
    element_patterns = {
        "genre": r'^[\w\-\s]+ audio quality',
        "frequency_balance": r'(highs|mids|lows|balanced)',
        "bass_treatment": r'(sub-bass|low-end|kick|bass)',
        "midrange": r'(midrange|leads|clarity)',
        "highs": r'(presence|air|sparkle|sheen)',
        "dynamics": r'(mastering|transient|pumping|compression)',
        "space": r'(reverb|delay|stereo|field)',
        "noise_floor": r'(noise|hiss|artifacts)',
    }

    detected = []
    for element, pattern in element_patterns.items():
        if re.search(pattern, style_text, re.IGNORECASE):
            detected.append(element)

    missing = [e for e in element_patterns.keys() if e not in detected]

    issues = []
    if word_count < 50:
        issues.append("Style prompt is quite short - may lack specificity")
    if "noise" not in style_text.lower() and "hiss" not in style_text.lower():
        issues.append("Consider adding noise floor quality statement")
    if "master" not in style_text.lower():
        issues.append("Consider adding mastering specifications")

    return {
        "word_count": word_count,
        "line_count": len(lines),
        "elements_detected": detected,
        "missing_elements": missing,
        "issues": issues,
        "coverage": f"{len(detected)}/{len(element_patterns)} elements",
        "assessment": "good" if len(issues) == 0 and len(detected) >= 6 else "needs improvement"
    }


def analyze_lyrics_output(lyrics_text: str) -> dict:
    """
    Analyze the Lyrics field (meta tags + structure) output.

    Returns analysis including:
    - Section count and types
    - Style block presence
    - Instrument descriptors quality
    - Flow and energy progression
    """
    lines = [l.strip() for l in lyrics_text.strip().split('\n') if l.strip()]

    # Check for [Style] block
    has_style_block = any('[Style]' in line or '[style]' in line.lower() for line in lines)

    # Extract meta tags
    meta_tag_pattern = r'\[([^\]]+)\]'
    all_tags = re.findall(meta_tag_pattern, lyrics_text)

    # Categorize tags
    section_tags = []
    style_tags = []

    section_types = ['intro', 'verse', 'pre-chorus', 'chorus', 'post-chorus',
                     'bridge', 'breakdown', 'buildup', 'drop', 'solo', 'outro', 'coda']

    for tag in all_tags:
        tag_lower = tag.lower()
        if 'style' in tag_lower:
            style_tags.append(tag)
        elif any(st in tag_lower for st in section_types):
            section_tags.append(tag)

    # Analyze section flow
    section_sequence = []
    for tag in section_tags:
        for st in section_types:
            if st in tag.lower():
                section_sequence.append(st)
                break

    # Check for instrument descriptors
    has_instruments = any(':' in tag for tag in section_tags)

    issues = []
    if not has_style_block:
        issues.append("Missing [Style] block at the beginning")
    if len(section_tags) < 3:
        issues.append("Very few sections - consider adding more structure")
    if not has_instruments:
        issues.append("No instrument descriptors in section tags")

    # Check for energy arc
    energy_issues = []
    if section_sequence:
        if section_sequence[0] not in ['intro']:
            energy_issues.append("Consider starting with [Intro]")
        if section_sequence[-1] not in ['outro', 'coda']:
            energy_issues.append("Consider ending with [Outro] or [Coda]")

    return {
        "has_style_block": has_style_block,
        "section_count": len(section_tags),
        "section_types": list(set(section_sequence)),
        "section_sequence": section_sequence,
        "has_instrument_descriptors": has_instruments,
        "issues": issues + energy_issues,
        "assessment": "good" if len(issues) == 0 else "needs improvement"
    }


def check_workflow_guidelines(aspect: str, output_type: str = "meta_tags") -> str:
    """
    Get Suno workflow best practices for a specific aspect.

    Args:
        aspect: The aspect to get guidelines for
        output_type: "meta_tags" or "audio_quality"
    """
    if output_type == "audio_quality":
        return get_audio_quality_guidelines(aspect)
    return get_meta_tag_guidelines(aspect)


def validate_workflow_output(style_text: str, lyrics_text: str) -> dict:
    """
    Validate both outputs and provide quality scores.

    Returns:
    - style_score (1-10)
    - lyrics_score (1-10)
    - overall_score (1-10)
    - suggestions for improvement
    """
    style_analysis = analyze_style_output(style_text)
    lyrics_analysis = analyze_lyrics_output(lyrics_text)

    # Score style output
    style_score = 10
    style_suggestions = []

    if style_analysis["assessment"] != "good":
        style_score -= 2
    if len(style_analysis["missing_elements"]) > 2:
        style_score -= 1
        style_suggestions.append(f"Add elements: {', '.join(style_analysis['missing_elements'][:3])}")
    for issue in style_analysis["issues"]:
        style_score -= 0.5
        style_suggestions.append(issue)

    # Score lyrics output
    lyrics_score = 10
    lyrics_suggestions = []

    if not lyrics_analysis["has_style_block"]:
        lyrics_score -= 2
        lyrics_suggestions.append("Add [Style] block at the beginning")
    if lyrics_analysis["section_count"] < 5:
        lyrics_score -= 1
        lyrics_suggestions.append("Add more sections for better structure")
    if not lyrics_analysis["has_instrument_descriptors"]:
        lyrics_score -= 1
        lyrics_suggestions.append("Add instrument descriptors to section tags (e.g., [Verse: acoustic guitar, mellow])")
    for issue in lyrics_analysis["issues"]:
        if issue not in lyrics_suggestions:
            lyrics_score -= 0.5
            lyrics_suggestions.append(issue)

    # Ensure scores are in valid range
    style_score = max(1, min(10, round(style_score)))
    lyrics_score = max(1, min(10, round(lyrics_score)))
    overall_score = round((style_score + lyrics_score) / 2)

    return {
        "style_score": style_score,
        "lyrics_score": lyrics_score,
        "overall_score": overall_score,
        "style_suggestions": style_suggestions,
        "lyrics_suggestions": lyrics_suggestions,
        "verdict": "excellent" if overall_score >= 8 else "good" if overall_score >= 6 else "needs work"
    }


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_style_output",
            "description": "Analyze the Style field (audio quality prompt) for completeness, detecting frequency balance, bass treatment, dynamics, and other audio quality elements.",
            "parameters": {
                "type": "object",
                "properties": {
                    "style_text": {
                        "type": "string",
                        "description": "The Style field text to analyze"
                    }
                },
                "required": ["style_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_lyrics_output",
            "description": "Analyze the Lyrics field (meta tags + structure) for section structure, instrument descriptors, and energy flow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lyrics_text": {
                        "type": "string",
                        "description": "The Lyrics field text to analyze"
                    }
                },
                "required": ["lyrics_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_workflow_guidelines",
            "description": "Get Suno workflow best practices. For meta tags: 'general', 'sections', 'instruments', 'transitions', 'anti_patterns'. For audio quality: 'general', 'genre_specific', 'mixing_terms'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "aspect": {
                        "type": "string",
                        "description": "The aspect to get guidelines for"
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["meta_tags", "audio_quality"],
                        "description": "Whether to get meta tag or audio quality guidelines"
                    }
                },
                "required": ["aspect", "output_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_workflow_output",
            "description": "Validate both Style and Lyrics outputs, providing scores (1-10) and suggestions for improvement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "style_text": {
                        "type": "string",
                        "description": "The Style field text"
                    },
                    "lyrics_text": {
                        "type": "string",
                        "description": "The Lyrics field text"
                    }
                },
                "required": ["style_text", "lyrics_text"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool and return the result as JSON string."""
    if tool_name == "analyze_style_output":
        result = analyze_style_output(arguments["style_text"])
    elif tool_name == "analyze_lyrics_output":
        result = analyze_lyrics_output(arguments["lyrics_text"])
    elif tool_name == "check_workflow_guidelines":
        result = check_workflow_guidelines(
            arguments["aspect"],
            arguments.get("output_type", "meta_tags")
        )
    elif tool_name == "validate_workflow_output":
        result = validate_workflow_output(
            arguments["style_text"],
            arguments["lyrics_text"]
        )
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    if isinstance(result, str):
        return result
    return json.dumps(result, indent=2)
