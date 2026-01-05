"""
Suno AI Prompt Knowledge Base
Curated best practices and guidelines for effective music generation prompts.
"""

SUNO_GUIDELINES = {
    "general": [
        "Keep prompts under 200 words for best results",
        "Use comma-separated descriptors",
        "Be specific about genre and sub-genre",
        "Combine multiple style influences for unique results",
        "Include production quality descriptors (professional, polished, studio quality)",
        "Suno responds well to emotional descriptors",
        "Layer descriptors: genre + mood + instrumentation + production",
    ],

    "tempo": [
        "Specify BPM ranges rather than exact numbers (around 90 BPM, approximately 120 BPM)",
        "Use tempo words: slow, mid-tempo, uptempo, fast, driving, relaxed",
        "Combine tempo with feel: 'slow and sultry', 'uptempo and energetic'",
        "For jazz: 'medium swing', 'slow ballad tempo', 'uptempo bebop'",
        "Groove descriptors help: 'laid-back tempo', 'driving rhythm', 'relaxed pace'",
    ],

    "mood": [
        "Emotional descriptors work well: melancholic, uplifting, dreamy, intense",
        "Atmosphere words: intimate, expansive, dark, bright, warm, cool",
        "Energy levels: mellow, chill, energetic, explosive, subdued",
        "Combine mood with texture: 'warm and intimate', 'dark and brooding'",
        "Time-of-day associations: 'late night', 'sunrise', 'midnight'",
        "Spatial descriptors: 'spacious', 'tight', 'airy', 'dense'",
    ],

    "arrangement": [
        "Specify intro style: 'gentle piano intro', 'drums enter gradually'",
        "Use build/dynamics hints: 'building intensity', 'dynamic contrast'",
        "Section hints: 'extended solo section', 'breakdown in the middle'",
        "Texture evolution: 'starts sparse, builds to full arrangement'",
        "Ending hints: 'fade out', 'dramatic ending', 'gentle resolution'",
        "Avoid 'no drums' - instead say 'piano-led intro' or 'rhythm section enters later'",
    ],

    "instruments": [
        "Be specific about instrument tones: 'warm Rhodes piano', 'punchy bass'",
        "Guitar descriptors: 'clean jazz guitar', 'warm hollow-body tone', 'chorus effect'",
        "Piano types: 'grand piano', 'Rhodes', 'Wurlitzer', 'acoustic piano'",
        "Drum descriptors: 'brushed drums', 'tight snare', 'deep kick', 'jazzy hi-hats'",
        "Bass: 'walking bass', 'groovy bass line', 'fretless bass', 'upright bass'",
        "Synths: 'analog synth pads', 'warm synth textures', 'vintage synth'",
        "Brass: 'muted trumpet', 'warm saxophone', 'lush brass section'",
    ],

    "production": [
        "Mix descriptors: 'warm analog mix', 'clean modern production', 'lo-fi texture'",
        "Space/reverb: 'spacious reverb', 'intimate dry sound', 'ambient atmosphere'",
        "Vintage vs modern: 'vintage recording', 'modern crisp production'",
        "Quality terms: 'professional', 'studio quality', 'polished', 'high fidelity'",
        "Character: 'organic feel', 'electronic polish', 'live band feel'",
    ],

    "genre_jazz": [
        "Sub-genres: smooth jazz, modal jazz, fusion, bebop, cool jazz, acid jazz",
        "Era references: '70s fusion', '80s smooth jazz', 'classic Blue Note era'",
        "Artist-adjacent (careful): 'Pat Metheny-esque', 'in the style of Weather Report'",
        "Jazz-specific: 'complex chord progressions', 'modal harmonies', 'jazz voicings'",
        "Improvisation hints: 'expressive solo', 'melodic improvisation'",
        "Rhythm section: 'swinging rhythm section', 'tight jazz trio'",
    ],

    "anti_patterns": [
        "AVOID negative terms: 'no drums', 'without vocals', 'not too fast' - these don't work",
        "AVOID overly long prompts (>300 words) - Suno may ignore parts",
        "AVOID contradictory descriptors: 'fast slow tempo', 'quiet loud'",
        "AVOID vague terms alone: 'good music', 'nice song' - be specific",
        "AVOID technical jargon Suno doesn't understand well",
        "INSTEAD of 'no X', specify what you DO want",
        "INSTEAD of negatives, use positive alternatives",
    ],

    "effective_keywords": [
        # Production
        "professional", "polished", "warm", "crisp", "vintage", "modern",
        "analog", "organic", "lush", "spacious", "intimate", "atmospheric",
        # Mood
        "mellow", "uplifting", "dreamy", "intense", "chill", "groovy",
        "soulful", "melancholic", "euphoric", "contemplative", "energetic",
        # Arrangement
        "building", "dynamic", "layered", "sparse", "full", "tight",
        "flowing", "rhythmic", "melodic", "harmonic", "textured",
        # Jazz-specific
        "modal", "fusion", "smooth", "swinging", "walking bass", "jazz voicings",
        "improvised", "expressive", "sophisticated", "complex harmonies",
    ],
}


def get_guidelines(aspect: str) -> str:
    """Get guidelines for a specific aspect of prompt writing."""
    if aspect in SUNO_GUIDELINES:
        return "\n".join(f"• {tip}" for tip in SUNO_GUIDELINES[aspect])
    return f"No specific guidelines for '{aspect}'. Available: {', '.join(SUNO_GUIDELINES.keys())}"


def get_all_guidelines() -> str:
    """Get all guidelines formatted as a comprehensive guide."""
    result = []
    for aspect, tips in SUNO_GUIDELINES.items():
        result.append(f"\n## {aspect.upper()}\n")
        result.extend(f"• {tip}" for tip in tips)
    return "\n".join(result)


def get_anti_patterns() -> list:
    """Get list of things to avoid in prompts."""
    return SUNO_GUIDELINES["anti_patterns"]


def get_effective_keywords() -> list:
    """Get list of keywords that work well with Suno."""
    return SUNO_GUIDELINES["effective_keywords"]
