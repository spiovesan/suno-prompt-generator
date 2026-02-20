# Phase 1: Profile Infrastructure

## Goal

Create the foundation for profile-based configuration: a new `profiles.py` data module, add missing moods to `data.py`, and wire the profile selector + change tracking into `app.py` with session persistence.

## Documentation References

- [Streamlit Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Developer Focus Mode Spec](../developer_focus_mode_spec.md)

---

## Step 1.1: Create `profiles.py`

**File:** `profiles.py`

### Purpose

Central data module for all Developer Focus Mode configuration: profile list, defaults, style presets, scenarios, tech stack tags, and helper functions. Kept as a single flat file to match the existing codebase structure (no `config/` or `templates/` directories).

### Implementation

```python
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
```

### Key Concepts

1. **Flat file structure** - Single `profiles.py` matches existing codebase (no directory nesting)
2. **Standard Suno section types** - Scenarios use Intro/Verse/Chorus/Bridge/Outro instead of custom names, for Suno compatibility
3. **Specific tech names** - `TECH_STACK_TAGS` uses concrete technology names (C++, PyTorch, Docker) not abstract categories
4. **DEV_FOCUS_DEFAULTS keys match data.py values** - e.g., `"Slow (60-80 BPM)"` matches `TEMPO_RANGES` exactly

---

## Step 1.2: Add 4 Moods to `data.py`

**File:** `data.py`

### Purpose

Developer scenarios reference moods (Calm, Focused, Relaxed, Creative) that don't exist in `MOOD_VARIATIONS`. These are universally useful moods, not developer-specific, so they belong in the global data module.

### Implementation

Add 4 entries to the `MOOD_VARIATIONS` dictionary (after the `"Searching"` entry, around line 426):

```python
    "Searching": "searching, harmonic tension, exploratory lines",
    "Calm": "calm, peaceful atmosphere, gentle and soothing",
    "Focused": "focused, clear atmosphere, steady and deliberate",
    "Relaxed": "relaxed, easygoing atmosphere, comfortable flow",
    "Creative": "creative, open atmosphere, inspiring and curious",
}
```

### Key Concepts

1. **Universal, not profile-specific** - These moods benefit all genres, not just Developer Focus
2. **Values follow existing pattern** - Format is `"adjective, descriptive phrase, quality"`
3. **Referenced by DEV_FOCUS_DEFAULTS** - `"mood": "Calm"` must match a key in `MOOD_VARIATIONS`
4. **Referenced by DEV_SCENARIOS** - Several scenarios use Focused, Creative, Relaxed

---

## Step 1.3: Add Profile Selector to `app.py`

**File:** `app.py`

### Purpose

Add imports from the new `profiles.py` module, then insert a profile selector dropdown at the top of the app (after title, before other UI). The selector drives all conditional rendering.

### Implementation

**Add import** (after existing imports, around line 22):

```python
from profiles import (
    PROFILES, ACTIVE_PROFILES, get_profile_defaults,
    get_dev_preset_names, get_dev_scenario_names, get_dev_scenario,
    TECH_STACK_TAGS, DEV_STYLE_PRESETS
)
```

**Pre-load profile from working session** (before the selectbox widget):

```python
# Pre-load profile from working session (must happen before widget instantiation)
if "_session_loaded" not in st.session_state and "profile_select" not in st.session_state:
    _working_preview = load_working_session()
    if _working_preview and "profile" in _working_preview:
        st.session_state["profile_select"] = _working_preview["profile"]
```

**Profile selector** (after `st.caption`, before Music Foundation):

```python
selected_profile = st.selectbox(
    "Profile",
    options=PROFILES,
    index=0,
    key="profile_select",
    help="Choose a purpose-specific profile. Developer Focus optimizes settings for coding sessions.",
    format_func=lambda x: f"{x}" if x in ACTIVE_PROFILES else f"{x}",
)

is_dev_focus = selected_profile == "Developer Focus"
```

### Key Concepts

1. **Pre-load before widget** - Streamlit requires session state values to be set *before* the widget that uses that key is instantiated. The `_working_preview` block loads the saved profile before `st.selectbox` renders.
2. **`is_dev_focus` boolean** - Used throughout the app for conditional UI (same pattern as `is_jazz`)
3. **`format_func`** - Future enhancement point for adding visual distinction to placeholder profiles
4. **`ACTIVE_PROFILES`** guards - Profile switching only applies defaults for functional profiles

---

## Step 1.4: Profile Change Tracking

**File:** `app.py`

### Purpose

When the user switches profiles, auto-populate form fields with the profile's defaults. Uses the same `_prev_*` tracking pattern already in the app for genre and key quality changes.

### Implementation

```python
# Profile change tracking (same pattern as genre tracking)
prev_profile = st.session_state.get("_prev_profile", None)
if prev_profile is not None and prev_profile != selected_profile:
    if selected_profile in ACTIVE_PROFILES and selected_profile != "General Purpose":
        defaults = get_profile_defaults(selected_profile)
        if defaults:
            # Set genre index (must delete widget key so index param takes effect)
            if defaults.get("genre") and defaults["genre"] in GENRES:
                st.session_state["loaded_genre_idx"] = GENRES.index(defaults["genre"])
                for key in ["genre_select", "style_preset_select", "style_influence_select"]:
                    if key in st.session_state:
                        del st.session_state[key]

            # Set other widget keys
            widget_map = {
                "tempo": "tempo_select",
                "mood": "mood_select",
                "time_sig": "time_sig_select",
                "key": "key_select",
                "mode": "mode_select",
            }
            for setting_key, widget_key in widget_map.items():
                if setting_key in defaults:
                    st.session_state[widget_key] = defaults[setting_key]

    # Clear dev-specific state when switching away
    if selected_profile != "Developer Focus":
        for key in ["scenario_select", "tech_stack_context", "tech_stack_tags"]:
            if key in st.session_state:
                del st.session_state[key]

    st.session_state["_prev_profile"] = selected_profile
    st.rerun()

st.session_state["_prev_profile"] = selected_profile
```

### Key Concepts

1. **Delete `genre_select` key** - Streamlit widget keys take precedence over the `index` parameter. Must delete the cached key so `loaded_genre_idx` is respected on rerun.
2. **`st.rerun()`** - Forces a fresh render cycle with the new widget values
3. **Cleanup on switch-away** - Dev-specific keys (scenario, tech context) are cleared when leaving Developer Focus
4. **Guard on prev_profile == None** - Prevents auto-applying on first render

---

## Step 1.5: Session Persistence

**File:** `app.py`

### Purpose

Persist profile and developer context in the working session auto-save, so the profile restores on page reload.

### Implementation

**In the session restore block** (inside `if "_session_loaded" not in st.session_state`):

```python
        # Restore developer context
        if "tech_stack_context" in working:
            st.session_state["tech_stack_context"] = working["tech_stack_context"]
        if "tech_stack_tags" in working:
            st.session_state["tech_stack_tags"] = working["tech_stack_tags"]
```

**In the working state auto-save** (at bottom of app):

```python
_working_state = {
    # ... existing keys ...

    # Profile
    "profile": selected_profile,
    "tech_stack_context": st.session_state.get("tech_stack_context", ""),
    "tech_stack_tags": st.session_state.get("tech_stack_tags", []),
}

save_working_session(_working_state)
```

**In the song save settings dict:**

```python
                    # Profile
                    "profile": selected_profile,
```

### Key Concepts

1. **Two persistence paths** - Working session (auto-save every render) and song history (manual save)
2. **Profile restored before widget** - The pre-load block in Step 1.3 handles this
3. **Tech context restored after widget** - These widgets appear later in the page, so restoring in the main session restore block is fine

---

## Verification Checklist

- [ ] App starts without import errors (`streamlit run app.py`)
- [ ] Profile selector visible at top of page with 5 options
- [ ] Selecting "Developer Focus" auto-sets Genre=Ambient, Tempo=Slow, Mood=Calm
- [ ] Selecting "General Purpose" doesn't change any values
- [ ] Placeholder profiles ("Study", "Meditation", "Creative Flow") show but don't trigger changes
- [ ] Page reload restores the selected profile
- [ ] "New Session" clears the profile back to General Purpose

## Next Phase

[Phase 2: Developer Presets](Phase2-DeveloperPresets.md)
