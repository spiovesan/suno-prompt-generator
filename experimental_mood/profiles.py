"""
Profile definitions for Suno Prompt Studio.
Contains profile configs, developer-specific presets, scenario templates,
and tech stack tags for the Developer Focus Mode.
"""

# =============================================================================
# PROFILES
# =============================================================================

PROFILES = [
    "General Purpose",
    "Developer Focus",
    "Study (coming soon)",
    "Meditation (coming soon)",
    "Creative Flow (coming soon)",
]

# Profiles that are actually functional (not placeholders)
ACTIVE_PROFILES = ["General Purpose", "Developer Focus"]

# Default form values when Developer Focus is activated
DEV_FOCUS_DEFAULTS = {
    "genre": "Ambient",
    "tempo": "Slow (60-80 BPM)",
    "mood": "Calm",
    "time_sig": "4/4",
    "key": "None",
    "mode": "Ionian (Major)",
    "style_preset": "None",
    "style_influence": "None",
    "progression": "None",
    "harmonic_rhythm": "None",
    "extensions": "None",
}


# =============================================================================
# DEVELOPER STYLE PRESETS (FR-3)
# =============================================================================

DEV_STYLE_PRESETS = {
    "None": "",
    "Deep Focus - Minimal": (
        "minimal techno foundation, no vocals, sustained pads, 65 BPM, "
        "layered textures, hypnotic pulse, deep focus optimization"
    ),
    "Deep Focus - Nature Ambient": (
        "forest ambience, water streams, gentle wind, minimal melodic elements, "
        "60 BPM, natural soundscape, no vocals"
    ),
    "Code Flow - Synthwave": (
        "retro synths, minimal percussion, nostalgic pads, no vocals, "
        "steady pulse, 75 BPM, 80s computer aesthetic, warm analog textures"
    ),
    "Debug Mode - Dark Ambient": (
        "deep bass drones, sparse industrial textures, metallic resonance, "
        "no vocals, 60 BPM, hypnotic and methodical, mechanical sounds"
    ),
    "Compilation Wait - Lo-fi": (
        "lo-fi hip hop beats, vinyl crackle, mellow piano, jazzy chords, "
        "no vocals, 70 BPM, relaxed groove, nostalgic warmth"
    ),
    "Neural Network Training": (
        "slowly evolving pads, generative patterns, algorithmic sequences, "
        "no vocals, 68 BPM, patient progression, computational aesthetic"
    ),
    "Late Night Coding": (
        "warm pads, gentle pulse, sustained energy, coffee shop ambience, "
        "no vocals, 72 BPM, comforting presence, night-time focus"
    ),
    "Morning Ramp-Up": (
        "rising pads, gentle awakening, brightening textures, "
        "minimal vocals possible, 65-80 BPM gradual increase, optimistic morning feel"
    ),
}


# =============================================================================
# DEVELOPER SCENARIOS (FR-4) - Using standard Suno section types
# =============================================================================

DEV_SCENARIOS = {
    "Deep Debugging Session": {
        "description": "Intense focus for tracking down complex bugs",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Focused",
        "style_preset": "Debug Mode - Dark Ambient",
        "sections": [
            {"type": "Intro", "instruments": "ambient pads, white noise undertone, mechanical hum"},
            {"type": "Verse", "instruments": "layered synths, minimal bass, steady pulse"},
            {"type": "Verse", "instruments": "sustained drones, subtle variations, hypnotic rhythm"},
            {"type": "Bridge", "instruments": "brief lift, gentle chimes, mental reset"},
            {"type": "Verse", "instruments": "deeper texture, sustained focus, warm bass"},
            {"type": "Outro", "instruments": "bright tones, gentle release, affirmative sound"},
        ],
    },
    "Refactoring Legacy Code": {
        "description": "Methodical music for systematic code improvement",
        "genre": "Ambient",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Calm",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "nostalgic pads, gentle start"},
            {"type": "Verse", "instruments": "layered textures, contemplative mood"},
            {"type": "Chorus", "instruments": "building energy, progressive layers"},
            {"type": "Verse", "instruments": "steady rhythm, methodical flow"},
            {"type": "Outro", "instruments": "satisfaction resolve, clean finish"},
        ],
    },
    "Architecture Planning": {
        "description": "Expansive thinking for high-level system design",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Creative",
        "style_preset": "Deep Focus - Nature Ambient",
        "sections": [
            {"type": "Intro", "instruments": "open space, wide pads"},
            {"type": "Verse", "instruments": "curious tones, question-like phrases"},
            {"type": "Bridge", "instruments": "structured patterns emerging, clarity"},
            {"type": "Verse", "instruments": "deeper layers, evolving complexity"},
            {"type": "Outro", "instruments": "clear, confident tones, resolution"},
        ],
    },
    "Long Compilation/Training Wait": {
        "description": "Relaxed vibes for waiting during builds or ML training",
        "genre": "Lo-fi",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Relaxed",
        "style_preset": "Compilation Wait - Lo-fi",
        "sections": [
            {"type": "Intro", "instruments": "warm pads, vinyl crackle"},
            {"type": "Verse", "instruments": "mellow beats, jazzy chords"},
            {"type": "Chorus", "instruments": "fuller texture, groove"},
            {"type": "Verse", "instruments": "subtle variations, steady groove"},
            {"type": "Outro", "instruments": "fade with comfort"},
        ],
    },
    "Data Analysis Flow": {
        "description": "For exploring datasets and finding patterns",
        "genre": "Techno",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Focused",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "digital textures, data-like sounds"},
            {"type": "Verse", "instruments": "repetitive motifs, algorithmic feel"},
            {"type": "Chorus", "instruments": "revelation moment, clarity"},
            {"type": "Verse", "instruments": "deeper patterns, sustained focus"},
            {"type": "Outro", "instruments": "synthesis, understanding"},
        ],
    },
    "UI/UX Design Work": {
        "description": "Creative flow for visual and interaction design",
        "genre": "Ambient",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Creative",
        "style_preset": "Code Flow - Synthwave",
        "sections": [
            {"type": "Intro", "instruments": "inspiring pads, color-like textures"},
            {"type": "Verse", "instruments": "evolving patterns, creative energy"},
            {"type": "Chorus", "instruments": "precise, detailed focus"},
            {"type": "Verse", "instruments": "iterative variations, flow state"},
            {"type": "Outro", "instruments": "satisfying resolution"},
        ],
    },
    "Documentation Writing": {
        "description": "Clear-headed focus for technical writing",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Calm",
        "style_preset": "Deep Focus - Nature Ambient",
        "sections": [
            {"type": "Intro", "instruments": "clear, open textures"},
            {"type": "Verse", "instruments": "steady, supportive pads"},
            {"type": "Bridge", "instruments": "structured, logical feel"},
            {"type": "Verse", "instruments": "maintained clarity, gentle flow"},
            {"type": "Outro", "instruments": "completion, peaceful close"},
        ],
    },
    "Code Review Session": {
        "description": "Attentive focus for reviewing others' code",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Focused",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "attentive pads, focused entry"},
            {"type": "Verse", "instruments": "detail-oriented textures, analytical"},
            {"type": "Bridge", "instruments": "balanced, thoughtful mood"},
            {"type": "Verse", "instruments": "steady attention, clear focus"},
            {"type": "Outro", "instruments": "decisive, clear resolution"},
        ],
    },
    "Late Night Coding": {
        "description": "Sustained energy for extended evening sessions",
        "genre": "Synthwave",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Dreamy",
        "style_preset": "Late Night Coding",
        "sections": [
            {"type": "Intro", "instruments": "warm synths, night ambience"},
            {"type": "Verse", "instruments": "sustained energy, gentle pulse"},
            {"type": "Chorus", "instruments": "full texture, in the zone"},
            {"type": "Verse", "instruments": "evolving patterns, nocturnal feel"},
            {"type": "Bridge", "instruments": "atmospheric break, distant echoes"},
            {"type": "Chorus", "instruments": "returning energy, warm resolution"},
            {"type": "Outro", "instruments": "gentle wind-down"},
        ],
    },
    "Morning Focus Ramp-Up": {
        "description": "Gradual energy building for starting your work day",
        "genre": "Lo-fi",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Relaxed",
        "style_preset": "Morning Ramp-Up",
        "sections": [
            {"type": "Intro", "instruments": "gentle awakening, soft start"},
            {"type": "Verse", "instruments": "energy building, brightening"},
            {"type": "Chorus", "instruments": "full presence, ready state"},
            {"type": "Verse", "instruments": "sustained momentum, warm groove"},
            {"type": "Outro", "instruments": "steady energy, smooth transition"},
        ],
    },
}


# =============================================================================
# TECH STACK TAGS (FR-5) - Specific tech names
# =============================================================================

TECH_STACK_TAGS = [
    # Languages
    "C++", "C#", "Python", "JavaScript", "TypeScript", "Java", "Rust", "Go",
    # Frameworks/Libraries
    "OpenCV", "PyTorch", "TensorFlow", "MFC", "WPF", "WinUI", "MAUI",
    # Domains
    "Computer Vision", "Deep Learning", "Machine Learning", "Robotics",
    "Web Development", "Desktop Apps", "Mobile Apps",
    # Tools
    "Visual Studio", "VS Code", "Git", "Azure DevOps", "Docker",
    # Activities
    "Debugging", "Refactoring", "Architecture", "Testing", "Documentation",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_profile_defaults(profile_name: str) -> dict | None:
    """
    Get default form values for a profile.
    Returns None for General Purpose (no overrides).
    """
    if profile_name == "Developer Focus":
        return DEV_FOCUS_DEFAULTS.copy()
    return None


def get_dev_preset_names() -> dict:
    """Get developer-specific style preset names and values."""
    return DEV_STYLE_PRESETS


def get_dev_scenario_names() -> list[str]:
    """Get list of developer scenario display names."""
    return list(DEV_SCENARIOS.keys())


def get_dev_scenario(name: str) -> dict | None:
    """Get a developer scenario config by name."""
    return DEV_SCENARIOS.get(name)
