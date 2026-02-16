# Developer Focus Mode - Implementation Specification

## Document Version: 1.0
**Date:** February 16, 2026  
**Target App:** Suno Prompt Studio (Streamlit)  
**Implementation Complexity:** Medium (2-3 hours for MVP)

---

## 🎯 Overview

This specification defines the implementation of "Developer Focus Mode" for the Suno Prompt Studio app. The feature adds a profile-based configuration system that pre-populates optimal settings for developers creating focus music.

### Goals
1. Enable specialized prompt generation for coding/developer workflows
2. Maintain existing app structure (no breaking changes)
3. Provide extensible architecture for future profiles (Study, Meditation, etc.)
4. Deliver immediate value with minimal code changes

### Non-Goals
- Complete app rewrite
- Separate standalone app
- Backend API changes
- Authentication/user accounts

---

## 📋 Feature Requirements

### FR-1: Profile Selector (MUST HAVE)
**Location:** Top of main app, immediately after title, before "Music Foundation" section

**Implementation:**
- Dropdown selector with 5 initial profiles
- Profile selection triggers auto-population of form fields
- Visual indicator showing active profile
- Help text explaining profile purpose

**Profiles (Initial Set):**
1. `General Purpose` (default, no changes to existing behavior)
2. `💻 Developer Focus` (new, primary focus of this spec)
3. `📚 Study & Concentration` (placeholder, future implementation)
4. `🧘 Meditation & Relaxation` (placeholder, future implementation)
5. `🎨 Creative Work` (placeholder, future implementation)

### FR-2: Developer Profile Auto-Configuration (MUST HAVE)
**Trigger:** When "💻 Developer Focus" is selected

**Auto-populated Fields:**

| Field | Current Options | Developer Default | Rationale |
|-------|----------------|-------------------|-----------|
| Genre | Jazz, Rock, etc. | Ambient | Optimal for concentration |
| Key | Various | None | Let AI decide |
| Mode | Ionian, Dorian, etc. | None or Aeolian (Minor) | Contemplative feel |
| Time Signature | 3/4, 4/4, etc. | 4/4 | Standard, steady |
| Tempo | Various ranges | Slow (60-80 BPM) | Deep focus range |
| Mood | Various | Calm | Concentration-friendly |
| Style Preset | Smooth Jazz, etc. | Deep Focus - Minimal | New preset |

### FR-3: Developer-Specific Style Presets (MUST HAVE)
**Location:** Add to existing "Style Preset" dropdown when Developer Focus is active

**New Presets to Add:**

```python
DEVELOPER_STYLE_PRESETS = {
    "Deep Focus - Minimal": {
        "description": "Pure concentration music with minimal distractions",
        "prompt": "minimal techno foundation, no vocals, sustained pads, 65 BPM, layered textures, hypnotic pulse, deep focus optimization"
    },
    
    "Deep Focus - Nature Ambient": {
        "description": "Nature-inspired ambient for organic focus",
        "prompt": "forest ambience, water streams, gentle wind, minimal melodic elements, 60 BPM, natural soundscape, no vocals"
    },
    
    "Code Flow - Synthwave": {
        "description": "Retro computing aesthetic for nostalgic coding",
        "prompt": "retro synths, minimal percussion, nostalgic pads, no vocals, steady pulse, 75 BPM, 80s computer aesthetic, warm analog textures"
    },
    
    "Debug Mode - Dark Ambient": {
        "description": "Deep, methodical atmosphere for intense debugging",
        "prompt": "deep bass drones, sparse industrial textures, metallic resonance, no vocals, 60 BPM, hypnotic and methodical, mechanical sounds"
    },
    
    "Compilation Wait - Lo-fi": {
        "description": "Relaxed beats for waiting during builds/training",
        "prompt": "lo-fi hip hop beats, vinyl crackle, mellow piano, jazzy chords, no vocals, 70 BPM, relaxed groove, nostalgic warmth"
    },
    
    "Neural Network Training": {
        "description": "Evolving textures for long ML training sessions",
        "prompt": "slowly evolving pads, generative patterns, algorithmic sequences, no vocals, 68 BPM, patient progression, computational aesthetic"
    },
    
    "Late Night Coding": {
        "description": "Sustained energy for extended sessions",
        "prompt": "warm pads, gentle pulse, sustained energy, coffee shop ambience, no vocals, 72 BPM, comforting presence, night-time focus"
    },
    
    "Morning Ramp-Up": {
        "description": "Gradual energy building for starting the day",
        "prompt": "rising pads, gentle awakening, brightening textures, minimal vocals possible, 65-80 BPM gradual increase, optimistic morning feel"
    }
}
```

### FR-4: Developer Scenario Templates (SHOULD HAVE)
**Location:** New section appearing only when Developer Focus profile is active

**UI Component:** Dropdown with pre-built developer workflow scenarios

**Scenarios:**

```python
DEVELOPER_SCENARIOS = {
    "🐛 Deep Debugging Session": {
        "title_template": "Debug Mode - {context}",
        "genre": "Minimal Techno",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Focused",
        "style_preset": "Debug Mode - Dark Ambient",
        "sections": [
            {"type": "Intro", "instruments": "ambient pads, white noise undertone, mechanical hum"},
            {"type": "Focus Zone", "instruments": "layered synths, minimal bass, steady pulse"},
            {"type": "Deep Dive", "instruments": "sustained drones, subtle variations, hypnotic rhythm"},
            {"type": "Resolution", "instruments": "bright tones, gentle release, affirmative sound"}
        ],
        "description": "For intense problem-solving and bug hunting"
    },
    
    "⚙️ Refactoring Legacy Code": {
        "title_template": "Refactor Flow - {context}",
        "genre": "Ambient",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Methodical",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "nostalgic pads, gentle start"},
            {"type": "Analysis", "instruments": "layered textures, contemplative mood"},
            {"type": "Reconstruction", "instruments": "building energy, progressive layers"},
            {"type": "Outro", "instruments": "satisfaction resolve, clean finish"}
        ],
        "description": "Methodical music for systematic code improvement"
    },
    
    "🧠 Architecture Planning": {
        "title_template": "Architect Mode - {context}",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Contemplative",
        "style_preset": "Deep Focus - Nature Ambient",
        "sections": [
            {"type": "Intro", "instruments": "open space, wide pads"},
            {"type": "Exploration", "instruments": "curious tones, question-like phrases"},
            {"type": "Crystallization", "instruments": "structured patterns emerging"},
            {"type": "Vision", "instruments": "clear, confident tones"}
        ],
        "description": "For high-level system design and planning"
    },
    
    "🔄 Long Compilation/Training Wait": {
        "title_template": "Patience Protocol - {context}",
        "genre": "Lo-fi",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Relaxed",
        "style_preset": "Compilation Wait - Lo-fi",
        "sections": [
            {"type": "Intro", "instruments": "warm pads, vinyl crackle"},
            {"type": "Verse", "instruments": "mellow beats, jazzy chords"},
            {"type": "Chorus", "instruments": "fuller texture, groove"},
            {"type": "Outro", "instruments": "fade with comfort"}
        ],
        "description": "Relaxed vibes for waiting periods"
    },
    
    "📊 Data Analysis Flow": {
        "title_template": "Data Dive - {context}",
        "genre": "Minimal Techno",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Analytical",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "digital textures, data-like sounds"},
            {"type": "Pattern Recognition", "instruments": "repetitive motifs, algorithmic feel"},
            {"type": "Insight", "instruments": "revelation moment, clarity"},
            {"type": "Outro", "instruments": "synthesis, understanding"}
        ],
        "description": "For exploring datasets and finding patterns"
    },
    
    "🎨 UI/UX Design Work": {
        "title_template": "Design Flow - {context}",
        "genre": "Ambient",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Creative",
        "style_preset": "Code Flow - Synthwave",
        "sections": [
            {"type": "Intro", "instruments": "inspiring pads, color-like textures"},
            {"type": "Iteration", "instruments": "evolving patterns, creative energy"},
            {"type": "Refinement", "instruments": "precise, detailed focus"},
            {"type": "Polish", "instruments": "satisfying resolution"}
        ],
        "description": "Creative flow for visual and interaction design"
    },
    
    "📝 Documentation Writing": {
        "title_template": "Doc Flow - {context}",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Clear-headed",
        "style_preset": "Deep Focus - Nature Ambient",
        "sections": [
            {"type": "Intro", "instruments": "clear, open textures"},
            {"type": "Writing Flow", "instruments": "steady, supportive pads"},
            {"type": "Organization", "instruments": "structured, logical feel"},
            {"type": "Outro", "instruments": "completion, clarity"}
        ],
        "description": "Clear-headed focus for technical writing"
    },
    
    "🔍 Code Review Session": {
        "title_template": "Review Mode - {context}",
        "genre": "Ambient",
        "tempo": "Slow (60-80 BPM)",
        "mood": "Attentive",
        "style_preset": "Deep Focus - Minimal",
        "sections": [
            {"type": "Intro", "instruments": "attentive pads, focused entry"},
            {"type": "Analysis", "instruments": "detail-oriented textures"},
            {"type": "Consideration", "instruments": "balanced, thoughtful mood"},
            {"type": "Conclusion", "instruments": "decisive, clear"}
        ],
        "description": "Attentive focus for reviewing others' code"
    },
    
    "🚀 Late Night Coding": {
        "title_template": "Night Shift - {context}",
        "genre": "Synthwave",
        "tempo": "Mid-tempo (80-110 BPM)",
        "mood": "Nocturnal",
        "style_preset": "Late Night Coding",
        "sections": [
            {"type": "Intro", "instruments": "warm synths, night ambience"},
            {"type": "Flow", "instruments": "sustained energy, gentle pulse"},
            {"type": "Peak Focus", "instruments": "full texture, in the zone"},
            {"type": "Outro", "instruments": "gentle wind-down"}
        ],
        "description": "Sustained energy for extended evening sessions"
    },
    
    "☕ Morning Focus Ramp-Up": {
        "title_template": "Morning Boot - {context}",
        "genre": "Lo-fi",
        "tempo": "Slow (60-80 BPM) → Mid-tempo (80-110 BPM)",
        "mood": "Awakening",
        "style_preset": "Morning Ramp-Up",
        "sections": [
            {"type": "Intro", "instruments": "gentle awakening, soft start"},
            {"type": "Caffeine Kick", "instruments": "energy building, brightening"},
            {"type": "System Online", "instruments": "full presence, ready state"},
            {"type": "Outro", "instruments": "sustained momentum"}
        ],
        "description": "Gradual energy building for starting your work day"
    }
}
```

### FR-5: Tech Stack Context (SHOULD HAVE)
**Location:** New section appearing only when Developer Focus profile is active

**UI Components:**
1. Text input: "What are you working on?" (optional)
2. Multi-select: Tech stack tags (optional)

**Tech Stack Tags:**
```python
TECH_STACK_TAGS = [
    # Languages
    "C++", "C#", "Python", "JavaScript", "TypeScript", "Java", "Rust", "Go",
    
    # Frameworks/Libraries (User's stack)
    "OpenCV", "PyTorch", "TensorFlow", "MFC", "WPF", "WinUI", "MAUI",
    
    # Domains
    "Computer Vision", "Deep Learning", "Machine Learning", "Robotics", 
    "Web Development", "Desktop Apps", "Mobile Apps",
    
    # Tools
    "Visual Studio", "VS Code", "Git", "Azure DevOps", "Docker",
    
    # Activities
    "Debugging", "Refactoring", "Architecture", "Testing", "Documentation"
]
```

**Behavior:**
- When context is provided, suggest a track title incorporating the context
- Example: Input "Refactoring legacy MFC code" → Suggest title: "Refactor Flow - MFC Modernization"
- Tags are appended to generated style field as subtle hints

### FR-6: Visual Indicators (SHOULD HAVE)
**Location:** Appears when Developer Focus profile is active

**Design:**
```html
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
            padding: 15px; border-radius: 8px; color: white; margin: 15px 0;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);'>
    <strong>💻 Developer Focus Mode Active</strong><br/>
    <small>Optimized for: No/minimal vocals • Deep focus • 60-80 BPM range • Ambient/Minimal genres • Sustained concentration</small>
</div>
```

---

## 🏗️ Architecture & Code Structure

### File Organization

```
suno_prompt_studio/
├── app.py                          # Main Streamlit app (MODIFY)
├── config/
│   ├── __init__.py
│   ├── profiles.py                 # NEW: Profile configurations
│   └── developer_config.py         # NEW: Developer-specific settings
├── templates/
│   ├── __init__.py
│   ├── developer_scenarios.py      # NEW: Pre-built dev templates
│   └── style_presets.py            # MODIFY: Add developer presets
└── utils/
    ├── __init__.py
    ├── prompt_generator.py         # MODIFY: Handle profile-aware generation
    └── profile_manager.py          # NEW: Profile state management
```

### Data Structures

#### Profile Configuration Schema
```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ProfileConfig:
    """Base configuration for a profile"""
    id: str
    name: str
    emoji: str
    description: str
    default_genre: str
    default_tempo: str
    default_mood: Optional[str]
    default_style_preset: str
    recommended_bpm_range: tuple
    vocal_preference: str  # "none", "minimal", "optional", "full"
    
@dataclass  
class SectionConfig:
    """Song section configuration"""
    type: str  # "Intro", "Verse", "Chorus", etc.
    instruments: str
    
@dataclass
class ScenarioTemplate:
    """Developer scenario template"""
    id: str
    name: str
    emoji: str
    title_template: str
    genre: str
    tempo: str
    mood: str
    style_preset: str
    sections: List[SectionConfig]
    description: str
```

#### Developer Profile Instance
```python
DEVELOPER_PROFILE = ProfileConfig(
    id="developer_focus",
    name="Developer Focus",
    emoji="💻",
    description="Optimized for coding, debugging, and technical work requiring sustained concentration",
    default_genre="Ambient",
    default_tempo="Slow (60-80 BPM)",
    default_mood="Calm",
    default_style_preset="Deep Focus - Minimal",
    recommended_bpm_range=(60, 80),
    vocal_preference="none"
)
```

---

## 🔄 User Flow

### Flow Diagram

```
User opens app
    ↓
Sees "Profile / Use Case" selector at top
    ↓
Selects "💻 Developer Focus"
    ↓
Visual indicator appears (purple gradient banner)
    ↓
Form fields auto-populate with developer-optimized defaults:
    - Genre: Ambient
    - Tempo: Slow (60-80 BPM)
    - Mood: Calm
    - Style Preset: Deep Focus - Minimal
    ↓
Developer-specific sections appear:
    - "Developer Scenario Templates" dropdown
    - "Tech Stack Context" (optional fields)
    ↓
[OPTIONAL] User selects scenario (e.g., "🐛 Deep Debugging Session")
    ↓
    - Auto-populates song structure sections
    - Suggests title template
    ↓
[OPTIONAL] User adds context: "Debugging PyTorch CUDA issues"
    ↓
    - Suggested title updates: "Debug Mode - PyTorch CUDA"
    ↓
User clicks "🎵 Generate"
    ↓
App generates optimized Style and Lyrics fields
    ↓
User copies outputs to Suno
    ↓
[OPTIONAL] User saves song with custom title
```

### Backward Compatibility

- **"General Purpose" profile** = existing app behavior (NO CHANGES)
- Profile selection persists in session state
- All existing features remain functional
- No breaking changes to existing user workflows

---

## 💻 Implementation Details

### Priority 1: Core Profile System (MUST HAVE - 1 hour)

**File: `config/profiles.py`**
```python
"""Profile configurations for different use cases"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ProfileConfig:
    id: str
    name: str
    emoji: str
    description: str
    default_genre: str
    default_tempo: str
    default_mood: Optional[str]
    default_style_preset: str

# Define all profiles
PROFILES = {
    "general": ProfileConfig(
        id="general",
        name="General Purpose",
        emoji="🎵",
        description="Standard mode with no pre-configuration",
        default_genre=None,  # No override
        default_tempo=None,
        default_mood=None,
        default_style_preset=None
    ),
    
    "developer": ProfileConfig(
        id="developer",
        name="Developer Focus",
        emoji="💻",
        description="Optimized for coding and technical work requiring sustained concentration",
        default_genre="Ambient",
        default_tempo="Slow (60-80 BPM)",
        default_mood="Calm",
        default_style_preset="Deep Focus - Minimal"
    ),
    
    "study": ProfileConfig(
        id="study",
        name="Study & Concentration",
        emoji="📚",
        description="For academic work and learning (future implementation)",
        default_genre="Classical",
        default_tempo="Slow (60-80 BPM)",
        default_mood="Focused",
        default_style_preset=None
    ),
    
    "meditation": ProfileConfig(
        id="meditation",
        name="Meditation & Relaxation",
        emoji="🧘",
        description="For mindfulness and relaxation (future implementation)",
        default_genre="Ambient",
        default_tempo="Very Slow (40-60 BPM)",
        default_mood="Peaceful",
        default_style_preset=None
    ),
    
    "creative": ProfileConfig(
        id="creative",
        name="Creative Work",
        emoji="🎨",
        description="For artistic and design work (future implementation)",
        default_genre="Indie",
        default_tempo="Mid-tempo (80-110 BPM)",
        default_mood="Inspired",
        default_style_preset=None
    )
}

def get_profile(profile_id: str) -> ProfileConfig:
    """Get profile configuration by ID"""
    return PROFILES.get(profile_id, PROFILES["general"])
```

**File: `app.py` (MODIFY - add after title)**
```python
import streamlit as st
from config.profiles import PROFILES, get_profile

# ... existing imports ...

# Add this right after st.title()
st.markdown("---")
st.markdown("### 🎯 Profile / Use Case")

profile_options = [
    f"{p.emoji} {p.name}" for p in PROFILES.values()
]

selected_profile_display = st.selectbox(
    "Choose a profile to pre-configure optimal settings",
    profile_options,
    help="Profiles automatically configure genre, tempo, mood, and structure for specific use cases",
    key="profile_selector"
)

# Extract profile ID from selection
selected_profile_id = selected_profile_display.split(" ", 1)[1].lower().replace(" ", "_").replace("&", "").replace("__", "_")
if selected_profile_id == "general_purpose":
    selected_profile_id = "general"
elif selected_profile_id == "developer_focus":
    selected_profile_id = "developer"
elif selected_profile_id == "study_concentration":
    selected_profile_id = "study"
elif selected_profile_id == "meditation_relaxation":
    selected_profile_id = "meditation"
elif selected_profile_id == "creative_work":
    selected_profile_id = "creative"

profile = get_profile(selected_profile_id)

# Store in session state for access throughout app
st.session_state['active_profile'] = profile

# Show visual indicator for developer mode
if profile.id == "developer":
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 15px; border-radius: 8px; color: white; margin: 15px 0;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);'>
        <strong>💻 Developer Focus Mode Active</strong><br/>
        <small>Optimized for: No/minimal vocals • Deep focus • 60-80 BPM range • Ambient/Minimal genres • Sustained concentration</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
```

### Priority 2: Auto-Population Logic (MUST HAVE - 30 minutes)

**File: `app.py` (MODIFY - in Music Foundation section)**
```python
# Get active profile
active_profile = st.session_state.get('active_profile', PROFILES["general"])

# Genre dropdown - use profile default if available
default_genre_index = 0
if active_profile.default_genre:
    try:
        default_genre_index = genre_options.index(active_profile.default_genre)
    except ValueError:
        default_genre_index = 0

selected_genre = st.selectbox(
    "Genre",
    genre_options,
    index=default_genre_index,
    key="genre_select",
    help="..." 
)

# Tempo dropdown - use profile default if available  
default_tempo_index = 0
if active_profile.default_tempo:
    try:
        default_tempo_index = tempo_options.index(active_profile.default_tempo)
    except ValueError:
        default_tempo_index = 0
        
selected_tempo = st.selectbox(
    "Tempo",
    tempo_options,
    index=default_tempo_index,
    key="tempo_select",
    help="..."
)

# Mood dropdown - use profile default if available
default_mood_index = 0  
if active_profile.default_mood:
    try:
        default_mood_index = mood_options.index(active_profile.default_mood)
    except ValueError:
        default_mood_index = 0
        
selected_mood = st.selectbox(
    "Mood",
    mood_options,
    index=default_mood_index,
    key="mood_select",
    help="..."
)
```

### Priority 3: Developer Style Presets (MUST HAVE - 30 minutes)

**File: `config/developer_config.py`**
```python
"""Developer Focus Mode specific configurations"""

DEVELOPER_STYLE_PRESETS = {
    "Deep Focus - Minimal": {
        "description": "Pure concentration music with minimal distractions",
        "prompt": "minimal techno foundation, no vocals, sustained pads, 65 BPM, layered textures, hypnotic pulse, deep focus optimization"
    },
    
    "Deep Focus - Nature Ambient": {
        "description": "Nature-inspired ambient for organic focus",
        "prompt": "forest ambience, water streams, gentle wind, minimal melodic elements, 60 BPM, natural soundscape, no vocals"
    },
    
    "Code Flow - Synthwave": {
        "description": "Retro computing aesthetic for nostalgic coding",
        "prompt": "retro synths, minimal percussion, nostalgic pads, no vocals, steady pulse, 75 BPM, 80s computer aesthetic, warm analog textures"
    },
    
    "Debug Mode - Dark Ambient": {
        "description": "Deep, methodical atmosphere for intense debugging",
        "prompt": "deep bass drones, sparse industrial textures, metallic resonance, no vocals, 60 BPM, hypnotic and methodical, mechanical sounds"
    },
    
    "Compilation Wait - Lo-fi": {
        "description": "Relaxed beats for waiting during builds/training",
        "prompt": "lo-fi hip hop beats, vinyl crackle, mellow piano, jazzy chords, no vocals, 70 BPM, relaxed groove, nostalgic warmth"
    },
    
    "Neural Network Training": {
        "description": "Evolving textures for long ML training sessions",
        "prompt": "slowly evolving pads, generative patterns, algorithmic sequences, no vocals, 68 BPM, patient progression, computational aesthetic"
    },
    
    "Late Night Coding": {
        "description": "Sustained energy for extended sessions",
        "prompt": "warm pads, gentle pulse, sustained energy, coffee shop ambience, no vocals, 72 BPM, comforting presence, night-time focus"
    },
    
    "Morning Ramp-Up": {
        "description": "Gradual energy building for starting the day",
        "prompt": "rising pads, gentle awakening, brightening textures, minimal vocals possible, 65-80 BPM gradual increase, optimistic morning feel"
    }
}

def get_style_presets_for_profile(profile_id: str) -> dict:
    """Return appropriate style presets based on active profile"""
    if profile_id == "developer":
        return DEVELOPER_STYLE_PRESETS
    else:
        return {}  # Return standard presets (existing behavior)
```

**File: `app.py` (MODIFY - Style Preset section)**
```python
from config.developer_config import get_style_presets_for_profile

# Get active profile
active_profile = st.session_state.get('active_profile', PROFILES["general"])

# Get base style presets (your existing presets)
base_presets = {
    "Smooth Jazz": "...",
    # ... your existing presets
}

# Get profile-specific presets
profile_presets = get_style_presets_for_profile(active_profile.id)

# Merge presets (profile presets appear first)
all_presets = {**profile_presets, **base_presets}

# Show preset dropdown
preset_options = ["None"] + list(all_presets.keys())

# Default to profile's default preset if available
default_preset_index = 0
if active_profile.default_style_preset and active_profile.default_style_preset in preset_options:
    default_preset_index = preset_options.index(active_profile.default_style_preset)

selected_preset = st.selectbox(
    "Style Preset",
    preset_options,
    index=default_preset_index,
    key="style_preset_select",
    help="Quick templates for common styles"
)

# Show preset description if developer preset
if selected_preset in profile_presets:
    st.caption(f"💡 {profile_presets[selected_preset]['description']}")
```

### Priority 4: Developer Scenarios (SHOULD HAVE - 1 hour)

**File: `templates/developer_scenarios.py`**
```python
"""Pre-built templates for common developer workflows"""

from dataclasses import dataclass
from typing import List

@dataclass
class SectionConfig:
    type: str
    instruments: str

@dataclass  
class DeveloperScenario:
    id: str
    name: str
    emoji: str
    title_template: str
    genre: str
    tempo: str
    mood: str
    style_preset: str
    sections: List[SectionConfig]
    description: str

DEVELOPER_SCENARIOS = {
    "debug_session": DeveloperScenario(
        id="debug_session",
        name="Deep Debugging Session",
        emoji="🐛",
        title_template="Debug Mode - {context}",
        genre="Minimal Techno",
        tempo="Slow (60-80 BPM)",
        mood="Focused",
        style_preset="Debug Mode - Dark Ambient",
        sections=[
            SectionConfig("Intro", "ambient pads, white noise undertone, mechanical hum"),
            SectionConfig("Focus Zone", "layered synths, minimal bass, steady pulse"),
            SectionConfig("Deep Dive", "sustained drones, subtle variations, hypnotic rhythm"),
            SectionConfig("Resolution", "bright tones, gentle release, affirmative sound")
        ],
        description="For intense problem-solving and bug hunting"
    ),
    
    "refactoring": DeveloperScenario(
        id="refactoring",
        name="Refactoring Legacy Code",
        emoji="⚙️",
        title_template="Refactor Flow - {context}",
        genre="Ambient",
        tempo="Mid-tempo (80-110 BPM)",
        mood="Methodical",
        style_preset="Deep Focus - Minimal",
        sections=[
            SectionConfig("Intro", "nostalgic pads, gentle start"),
            SectionConfig("Analysis", "layered textures, contemplative mood"),
            SectionConfig("Reconstruction", "building energy, progressive layers"),
            SectionConfig("Outro", "satisfaction resolve, clean finish")
        ],
        description="Methodical music for systematic code improvement"
    ),
    
    "architecture": DeveloperScenario(
        id="architecture",
        name="Architecture Planning",
        emoji="🧠",
        title_template="Architect Mode - {context}",
        genre="Ambient",
        tempo="Slow (60-80 BPM)",
        mood="Contemplative",
        style_preset="Deep Focus - Nature Ambient",
        sections=[
            SectionConfig("Intro", "open space, wide pads"),
            SectionConfig("Exploration", "curious tones, question-like phrases"),
            SectionConfig("Crystallization", "structured patterns emerging"),
            SectionConfig("Vision", "clear, confident tones")
        ],
        description="For high-level system design and planning"
    ),
    
    "compilation_wait": DeveloperScenario(
        id="compilation_wait",
        name="Long Compilation/Training Wait",
        emoji="🔄",
        title_template="Patience Protocol - {context}",
        genre="Lo-fi",
        tempo="Mid-tempo (80-110 BPM)",
        mood="Relaxed",
        style_preset="Compilation Wait - Lo-fi",
        sections=[
            SectionConfig("Intro", "warm pads, vinyl crackle"),
            SectionConfig("Verse", "mellow beats, jazzy chords"),
            SectionConfig("Chorus", "fuller texture, groove"),
            SectionConfig("Outro", "fade with comfort")
        ],
        description="Relaxed vibes for waiting periods"
    ),
    
    "data_analysis": DeveloperScenario(
        id="data_analysis",
        name="Data Analysis Flow",
        emoji="📊",
        title_template="Data Dive - {context}",
        genre="Minimal Techno",
        tempo="Mid-tempo (80-110 BPM)",
        mood="Analytical",
        style_preset="Deep Focus - Minimal",
        sections=[
            SectionConfig("Intro", "digital textures, data-like sounds"),
            SectionConfig("Pattern Recognition", "repetitive motifs, algorithmic feel"),
            SectionConfig("Insight", "revelation moment, clarity"),
            SectionConfig("Outro", "synthesis, understanding")
        ],
        description="For exploring datasets and finding patterns"
    ),
    
    "ui_design": DeveloperScenario(
        id="ui_design",
        name="UI/UX Design Work",
        emoji="🎨",
        title_template="Design Flow - {context}",
        genre="Ambient",
        tempo="Mid-tempo (80-110 BPM)",
        mood="Creative",
        style_preset="Code Flow - Synthwave",
        sections=[
            SectionConfig("Intro", "inspiring pads, color-like textures"),
            SectionConfig("Iteration", "evolving patterns, creative energy"),
            SectionConfig("Refinement", "precise, detailed focus"),
            SectionConfig("Polish", "satisfying resolution")
        ],
        description="Creative flow for visual and interaction design"
    ),
    
    "documentation": DeveloperScenario(
        id="documentation",
        name="Documentation Writing",
        emoji="📝",
        title_template="Doc Flow - {context}",
        genre="Ambient",
        tempo="Slow (60-80 BPM)",
        mood="Clear-headed",
        style_preset="Deep Focus - Nature Ambient",
        sections=[
            SectionConfig("Intro", "clear, open textures"),
            SectionConfig("Writing Flow", "steady, supportive pads"),
            SectionConfig("Organization", "structured, logical feel"),
            SectionConfig("Outro", "completion, clarity")
        ],
        description="Clear-headed focus for technical writing"
    ),
    
    "code_review": DeveloperScenario(
        id="code_review",
        name="Code Review Session",
        emoji="🔍",
        title_template="Review Mode - {context}",
        genre="Ambient",
        tempo="Slow (60-80 BPM)",
        mood="Attentive",
        style_preset="Deep Focus - Minimal",
        sections=[
            SectionConfig("Intro", "attentive pads, focused entry"),
            SectionConfig("Analysis", "detail-oriented textures"),
            SectionConfig("Consideration", "balanced, thoughtful mood"),
            SectionConfig("Conclusion", "decisive, clear")
        ],
        description="Attentive focus for reviewing others' code"
    ),
    
    "late_night": DeveloperScenario(
        id="late_night",
        name="Late Night Coding",
        emoji="🚀",
        title_template="Night Shift - {context}",
        genre="Synthwave",
        tempo="Mid-tempo (80-110 BPM)",
        mood="Nocturnal",
        style_preset="Late Night Coding",
        sections=[
            SectionConfig("Intro", "warm synths, night ambience"),
            SectionConfig("Flow", "sustained energy, gentle pulse"),
            SectionConfig("Peak Focus", "full texture, in the zone"),
            SectionConfig("Outro", "gentle wind-down")
        ],
        description="Sustained energy for extended evening sessions"
    ),
    
    "morning_rampup": DeveloperScenario(
        id="morning_rampup",
        name="Morning Focus Ramp-Up",
        emoji="☕",
        title_template="Morning Boot - {context}",
        genre="Lo-fi",
        tempo="Slow (60-80 BPM)",
        mood="Awakening",
        style_preset="Morning Ramp-Up",
        sections=[
            SectionConfig("Intro", "gentle awakening, soft start"),
            SectionConfig("Caffeine Kick", "energy building, brightening"),
            SectionConfig("System Online", "full presence, ready state"),
            SectionConfig("Outro", "sustained momentum")
        ],
        description="Gradual energy building for starting your work day"
    )
}

def get_scenario(scenario_id: str) -> DeveloperScenario:
    """Get scenario by ID"""
    return DEVELOPER_SCENARIOS.get(scenario_id)
```

**File: `app.py` (ADD - Developer-specific section)**
```python
from templates.developer_scenarios import DEVELOPER_SCENARIOS, get_scenario

# Show developer scenarios section only when developer profile is active
if active_profile.id == "developer":
    st.markdown("---")
    st.markdown("### 🎯 Developer Scenario Templates")
    st.caption("Pre-configured templates for common developer workflows")
    
    scenario_options = ["Select a scenario..."] + [
        f"{s.emoji} {s.name}" for s in DEVELOPER_SCENARIOS.values()
    ]
    
    selected_scenario_display = st.selectbox(
        "Quick Scenario Templates",
        scenario_options,
        key="dev_scenario_select",
        help="Load pre-configured settings for common coding activities"
    )
    
    if selected_scenario_display != "Select a scenario...":
        # Extract scenario ID
        scenario_name = selected_scenario_display.split(" ", 1)[1]
        scenario = None
        for s in DEVELOPER_SCENARIOS.values():
            if s.name == scenario_name:
                scenario = s
                break
        
        if scenario:
            st.info(f"💡 {scenario.description}")
            
            # Button to apply scenario
            if st.button(f"Apply {scenario.emoji} {scenario.name}", key="apply_scenario"):
                # Update form fields with scenario settings
                st.session_state['scenario_genre'] = scenario.genre
                st.session_state['scenario_tempo'] = scenario.tempo
                st.session_state['scenario_mood'] = scenario.mood
                st.session_state['scenario_preset'] = scenario.style_preset
                st.session_state['scenario_sections'] = scenario.sections
                st.session_state['scenario_title_template'] = scenario.title_template
                
                st.success(f"✅ Applied scenario: {scenario.name}")
                st.rerun()
```

### Priority 5: Tech Stack Context (SHOULD HAVE - 45 minutes)

**File: `app.py` (ADD - Developer context section)**
```python
# Show tech context section only when developer profile is active
if active_profile.id == "developer":
    st.markdown("---")
    st.markdown("### 🔧 Developer Context (Optional)")
    st.caption("Add context to generate more tailored prompts and titles")
    
    # What are you working on?
    dev_context = st.text_input(
        "What are you working on?",
        placeholder="e.g., Refactoring legacy C++ code, Debugging PyTorch training, Building WPF UI",
        key="dev_context_input",
        help="Describe your current task to generate contextual track titles"
    )
    
    # Tech stack tags
    TECH_STACK_TAGS = [
        "C++", "C#", "Python", "JavaScript", "TypeScript", "Java", "Rust", "Go",
        "OpenCV", "PyTorch", "TensorFlow", "MFC", "WPF", "WinUI", "MAUI",
        "Computer Vision", "Deep Learning", "Machine Learning", "Robotics",
        "Web Development", "Desktop Apps", "Mobile Apps",
        "Visual Studio", "VS Code", "Git", "Azure DevOps", "Docker",
        "Debugging", "Refactoring", "Architecture", "Testing", "Documentation"
    ]
    
    selected_tech_tags = st.multiselect(
        "Tech Stack Tags",
        TECH_STACK_TAGS,
        key="tech_tags_select",
        help="Select relevant technologies to add context to your track"
    )
    
    # Generate suggested title if context provided
    if dev_context or selected_tech_tags:
        suggested_title = ""
        
        # Use scenario title template if available
        if 'scenario_title_template' in st.session_state:
            template = st.session_state['scenario_title_template']
            if dev_context:
                suggested_title = template.replace("{context}", dev_context)
            elif selected_tech_tags:
                suggested_title = template.replace("{context}", " + ".join(selected_tech_tags[:2]))
        else:
            # Generate generic title
            if dev_context:
                suggested_title = f"Focus Flow - {dev_context}"
            elif selected_tech_tags:
                suggested_title = f"Code Session - {' + '.join(selected_tech_tags[:2])}"
        
        if suggested_title:
            st.caption(f"💡 **Suggested Track Title:** {suggested_title}")
            
            # Store for use in save section
            st.session_state['suggested_title'] = suggested_title
```

---

## 📊 Testing Checklist

### Functional Tests
- [ ] Profile selector appears at top of app
- [ ] "General Purpose" profile maintains existing behavior (no changes)
- [ ] "Developer Focus" profile auto-populates correct defaults
- [ ] Visual indicator appears only for developer profile
- [ ] Developer style presets appear in dropdown
- [ ] Developer scenarios section appears only in developer mode
- [ ] Tech context section appears only in developer mode
- [ ] Scenario application updates form fields correctly
- [ ] Context input generates appropriate title suggestions
- [ ] Generated outputs incorporate developer-specific settings
- [ ] Save functionality works with suggested titles
- [ ] Batch generation works with developer profile

### Edge Cases
- [ ] Switching between profiles updates UI correctly
- [ ] Profile selection persists during session
- [ ] App doesn't break if profile config is missing
- [ ] Long context text doesn't break UI
- [ ] Many tech tags selected doesn't break UI
- [ ] Scenario with missing fields handles gracefully

### Backward Compatibility
- [ ] Existing users see no changes with "General Purpose" selected
- [ ] All existing features remain functional
- [ ] No breaking changes to saved song format
- [ ] No breaking changes to generated output format

---

## 🚀 Deployment Strategy

### Phase 1: MVP Deployment
**Deploy:** Priority 1-3 features (Core profile system, auto-population, style presets)
**Timeline:** Deploy as soon as MVP is tested
**Risk:** Low - minimal changes to existing code

### Phase 2: Enhanced Features  
**Deploy:** Priority 4-5 features (Scenarios, tech context)
**Timeline:** 1-2 weeks after MVP
**Risk:** Low-medium - new sections but isolated

### Phase 3: Future Enhancements
**Features:**
- LLM-powered context analysis
- Community template sharing
- More profiles (Study, Meditation, etc.)
- Analytics and usage tracking

---

## 📈 Success Metrics

### Quantitative
- Profile adoption rate (% of sessions using non-General profile)
- Developer profile usage (% of total profile selections)
- Scenario template usage (% of developer sessions)
- Generated tracks with developer profile (count)
- Average session time in developer mode vs. general mode

### Qualitative  
- User feedback on developer-specific features
- Community engagement (shares, mentions)
- Feature requests related to developer mode
- User-submitted scenario templates

---

## 🎨 Marketing & Positioning

### Messaging
**Primary:** "AI-generated flow states for developers"

**Secondary:** "Built by a developer, for developers - using open-source prompt engineering"

### Key Differentiators
1. **Not generic meditation music** - Specifically designed for coding workflows
2. **Transparent methodology** - Show the prompts, teach the process
3. **Developer credibility** - Built with tech stack developers actually use
4. **Free and open-source** - Community-driven tool

### Launch Strategy
1. **Soft launch:** Deploy feature, announce in existing user base
2. **Community seeding:** Share in developer communities (Reddit /r/programming, HN, Twitter)
3. **Content creation:** Blog post explaining the methodology
4. **Suno profile update:** Create developer-focused tracks showcasing the feature
5. **Feedback loop:** Gather suggestions for additional scenarios/presets

### Example Social Media Post
```
🎵 New: Developer Focus Mode in Suno Prompt Studio

I built a profile system for generating focus music specifically for coding:
• Pre-configured for deep work (60-80 BPM, ambient/minimal)
• 10 developer scenarios (debugging, refactoring, late-night coding)
• Tech stack context (add C++, PyTorch, etc. to customize)
• All open-source

Try it: https://suno-prompt-generator.streamlit.app/
Made by a dev who uses OpenCV, PyTorch, and drinks too much coffee ☕

#developer #coding #focusmusic #AImusic
```

---

## 🔮 Future Enhancements (Out of Scope for V1)

### V2 Features
- **LLM Context Analysis:** Use OpenAI to analyze dev context and generate highly specific prompts
- **Language-Specific Profiles:** Sub-profiles for C++, Python, etc. with unique aesthetics
- **Time-of-Day Optimization:** Morning, afternoon, evening, late-night variations
- **IDE Integration:** VS Code extension to generate music based on current file/project

### V3 Features
- **Community Templates:** User-submitted scenario templates
- **A/B Testing:** Let users vote on which presets work best
- **Spotify/YouTube Export:** Generate playlists from saved tracks
- **Analytics Dashboard:** Track which scenarios you use most

### V4 Features
- **Real-Time Adaptation:** Music that changes based on coding activity (fast typing = higher energy)
- **Pomodoro Integration:** Built-in timer with music state changes
- **Team Collaboration:** Shared focus sessions with synchronized music
- **ML-Powered Optimization:** Learn from user preferences to auto-generate personalized presets

---

## 📝 Notes for Claude Code

### Implementation Tips
1. **Start with Profile System:** Get the basic profile selector working first before adding specialized features
2. **Use Session State:** Leverage Streamlit's session state for profile persistence
3. **Modular Design:** Keep developer-specific code in separate modules for easy maintenance
4. **Progressive Enhancement:** Each priority level builds on the previous, can deploy incrementally
5. **Preserve Existing Behavior:** "General Purpose" profile = zero changes to current app

### Potential Issues
- **Dropdown Index Handling:** Careful with dropdown default index when profile changes
- **Session State Management:** Clear old scenario state when switching profiles
- **UI Reflow:** Conditional sections may cause layout shifts, test thoroughly
- **Long Text Fields:** Context input needs validation for reasonable length

### Code Style
- Follow existing app's code style and conventions
- Use type hints where possible
- Add docstrings to new functions
- Comment complex logic, especially profile switching

### Testing Approach
1. Test "General Purpose" profile first (should be unchanged)
2. Test profile switching multiple times in same session
3. Test each developer feature in isolation
4. Test complete developer workflow end-to-end
5. Test edge cases (missing data, long inputs, etc.)

---

## 🏁 Summary

This specification provides a complete implementation guide for adding Developer Focus Mode to the Suno Prompt Studio app. The design is:

✅ **Backward Compatible:** Existing users see no changes  
✅ **Extensible:** Architecture supports future profiles (Study, Meditation, etc.)  
✅ **Incremental:** Can deploy in phases (MVP → Enhanced → Future)  
✅ **Well-Structured:** Modular code organization for maintainability  
✅ **User-Focused:** Solves real developer pain points with specific workflows

**MVP Scope:** Priority 1-3 (Profile system, auto-population, style presets)  
**Estimated Implementation Time:** 2-3 hours for experienced developer  
**Risk Level:** Low (minimal changes to existing codebase)

Ready for implementation in Claude Code! 🚀
