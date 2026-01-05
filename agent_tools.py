"""
Agent tools for the Suno Prompt Refiner.
These functions are called by the OpenAI Assistant to analyze and refine prompts.
"""

import json
from suno_knowledge import (
    get_guidelines,
    get_anti_patterns,
    get_effective_keywords,
    SUNO_GUIDELINES
)


def analyze_prompt(prompt: str) -> dict:
    """
    Analyze a prompt for structure, keywords, and potential issues.

    Returns analysis including:
    - Word count and length assessment
    - Detected categories (mood, tempo, instruments, etc.)
    - Missing elements
    - Potential issues
    """
    words = prompt.split()
    word_count = len(words)

    # Check for effective keywords
    effective = get_effective_keywords()
    found_keywords = [kw for kw in effective if kw.lower() in prompt.lower()]

    # Check for anti-patterns
    anti_patterns = get_anti_patterns()
    issues = []

    # Check for negative words
    negative_indicators = ["no ", "without ", "not ", "don't ", "avoid "]
    for neg in negative_indicators:
        if neg in prompt.lower():
            issues.append(f"Contains negative term '{neg.strip()}' - Suno ignores negatives")

    # Check length
    if word_count > 200:
        issues.append(f"Prompt is {word_count} words - consider trimming to under 200")
    elif word_count < 10:
        issues.append("Prompt is very short - consider adding more descriptors")

    # Detect categories present
    categories_detected = []
    category_keywords = {
        "tempo": ["bpm", "tempo", "slow", "fast", "uptempo", "mid-tempo"],
        "mood": ["mellow", "uplifting", "dark", "bright", "warm", "intimate", "energetic"],
        "instruments": ["piano", "guitar", "bass", "drums", "synth", "brass", "saxophone"],
        "production": ["mix", "reverb", "analog", "vintage", "modern", "polished"],
        "arrangement": ["intro", "build", "dynamic", "sparse", "full", "solo"],
        "genre": ["jazz", "fusion", "smooth", "modal", "bebop", "funk", "soul"],
    }

    for category, keywords in category_keywords.items():
        if any(kw in prompt.lower() for kw in keywords):
            categories_detected.append(category)

    # Identify missing categories
    all_categories = list(category_keywords.keys())
    missing = [cat for cat in all_categories if cat not in categories_detected]

    return {
        "word_count": word_count,
        "length_assessment": "good" if 20 <= word_count <= 200 else "needs adjustment",
        "effective_keywords_found": found_keywords,
        "categories_detected": categories_detected,
        "missing_categories": missing,
        "issues": issues,
        "overall_assessment": "needs improvement" if issues or len(missing) > 3 else "good foundation"
    }


def check_suno_guidelines(aspect: str) -> str:
    """
    Get Suno best practices for a specific aspect.

    Available aspects: general, tempo, mood, arrangement, instruments,
    production, genre_jazz, anti_patterns, effective_keywords
    """
    return get_guidelines(aspect)


def validate_prompt(prompt: str) -> dict:
    """
    Validate a refined prompt and provide a quality score.

    Returns:
    - score (1-10)
    - strengths
    - weaknesses
    - suggestions for improvement
    """
    analysis = analyze_prompt(prompt)

    score = 10
    strengths = []
    weaknesses = []
    suggestions = []

    # Score based on length
    if analysis["length_assessment"] == "good":
        strengths.append("Good prompt length")
    else:
        score -= 1
        weaknesses.append(f"Length issue: {analysis['word_count']} words")
        if analysis["word_count"] > 200:
            suggestions.append("Trim to under 200 words")
        else:
            suggestions.append("Add more descriptive terms")

    # Score based on issues
    for issue in analysis["issues"]:
        score -= 1
        weaknesses.append(issue)
        if "negative" in issue.lower():
            suggestions.append("Replace negative terms with positive alternatives")

    # Score based on keyword usage
    keyword_count = len(analysis["effective_keywords_found"])
    if keyword_count >= 5:
        strengths.append(f"Good use of effective keywords ({keyword_count} found)")
    elif keyword_count >= 2:
        score -= 0.5
        suggestions.append("Consider adding more Suno-effective keywords")
    else:
        score -= 1
        weaknesses.append("Few effective keywords detected")
        suggestions.append("Add descriptors like: warm, lush, groovy, atmospheric, polished")

    # Score based on category coverage
    detected = len(analysis["categories_detected"])
    if detected >= 5:
        strengths.append(f"Excellent category coverage ({detected}/6)")
    elif detected >= 3:
        strengths.append(f"Good category coverage ({detected}/6)")
        suggestions.append(f"Consider adding: {', '.join(analysis['missing_categories'][:2])}")
    else:
        score -= 1
        weaknesses.append(f"Limited category coverage ({detected}/6)")
        suggestions.append(f"Add elements for: {', '.join(analysis['missing_categories'])}")

    # Ensure score is in valid range
    score = max(1, min(10, round(score)))

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "verdict": "excellent" if score >= 8 else "good" if score >= 6 else "needs work"
    }


# Tool definitions for OpenAI Assistants API
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_prompt",
            "description": "Analyze a music prompt for structure, keywords, detected categories, and potential issues. Use this first to understand the input prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The music prompt to analyze"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_suno_guidelines",
            "description": "Get Suno AI best practices for a specific aspect. Available aspects: general, tempo, mood, arrangement, instruments, production, genre_jazz, anti_patterns, effective_keywords",
            "parameters": {
                "type": "object",
                "properties": {
                    "aspect": {
                        "type": "string",
                        "description": "The aspect to get guidelines for (e.g., 'tempo', 'mood', 'arrangement')"
                    }
                },
                "required": ["aspect"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_prompt",
            "description": "Validate a refined prompt and get a quality score (1-10) with detailed feedback. Use this after refining to check quality.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The refined prompt to validate"
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool and return the result as JSON string."""
    if tool_name == "analyze_prompt":
        result = analyze_prompt(arguments["prompt"])
    elif tool_name == "check_suno_guidelines":
        result = check_suno_guidelines(arguments["aspect"])
    elif tool_name == "validate_prompt":
        result = validate_prompt(arguments["prompt"])
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result, indent=2)
