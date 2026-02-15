# Widget State Persistence Feature

## Problem Statement

Currently, when the user refreshes the browser (F5), all widget state is lost because Streamlit's `st.session_state` is in-memory only per connection. A refresh creates a new connection, losing:
- All Music Foundation selections (genre, key, mode, tempo, time signature, mood)
- All Options selections (preset, influence, harmony options)
- Song structure sections and instruments
- Pasted lyrics
- Generated/refined outputs

## Two Approaches Analyzed

### Option A: Persist Across F5 Refresh (Auto-Save)

**Mechanism:** Save current state to a JSON file automatically, load on app startup.

**Pros:**
- Seamless UX - user doesn't have to manually save
- Survives accidental refresh
- No extra button clicks

**Cons:**
- Requires file I/O on every state change (performance)
- Could cause confusion if user wants to start fresh
- Streamlit limitations make this complex (no native persistence)
- Need debouncing to avoid excessive writes

### Option B: Extend Song Saving (Recommended)

**Mechanism:** Enhance the existing "Save Song" feature to capture ALL current UI state, not just generated outputs.

**Pros:**
- Uses existing infrastructure (storage.py)
- Explicit user action - predictable behavior
- Can save multiple named states
- Already has UI for loading saved songs
- Simpler implementation

**Cons:**
- User must manually save before refresh
- Requires awareness that state is not auto-saved

---

## Recommended Solution: Hybrid Approach

Implement **both** mechanisms:
1. **Auto-Save Working Session** - Silently save to `working_session.json` on every widget change
2. **Enhanced Song Save** - Capture all state fields when user saves a song

---

## User Decisions

- **Auto-save**: On every widget change (immediate persistence)
- **Clear Session**: Yes, add "New Session" button in sidebar

---

## Implementation Plan

### Phase 1: Enhance Song Save to Capture All State

**File: `app.py`**

Update the settings dict to include ALL state (line ~984):

```python
settings = {
    # Music Foundation
    "genre": selected_genre,
    "key": selected_key,
    "mode": selected_mode,
    "tempo": selected_tempo,
    "time_sig": selected_time_sig,
    "mood": selected_mood,

    # Options
    "style_preset": selected_preset,
    "style_influence": selected_influence,
    "progression": selected_progression,
    "harmonic_rhythm": selected_harmonic_rhythm,
    "extensions": selected_extensions,

    # Song Structure
    "sections": st.session_state.sections,

    # NEW: Sidebar options
    "use_llm": use_llm,
    "replace_guitar": replace_guitar,
    "auto_fill_sections": st.session_state.get("auto_fill_sections", True),
    "lyrics_sync_mode": st.session_state.get("lyrics_sync_mode", "Smart merge"),

    # NEW: Lyrics content
    "suno_lyrics": suno_lyrics,
    "lyric_template": selected_lyric_template,
}
```

**File: `storage.py`**

No changes needed - already handles arbitrary settings dict.

**File: `app.py` - Load Song**

Enhance the load logic to restore all fields (lines ~206-210):

```python
if "loaded_song" in st.session_state:
    loaded = st.session_state.pop("loaded_song")

    # Map settings to widget keys for selectboxes
    key_mapping = {
        "genre": ("genre_select", GENRES),
        "key": ("key_select", list(all_keys.keys())),
        "mode": ("mode_select", list(MODES.keys())),
        "tempo": ("tempo_select", list(TEMPO_RANGES.keys())),
        "time_sig": ("time_sig_select", list(TIME_SIGNATURES.keys())),
        "mood": ("mood_select", list(MOOD_VARIATIONS.keys())),
    }

    for setting_key, (widget_key, options) in key_mapping.items():
        if setting_key in loaded:
            try:
                idx = options.index(loaded[setting_key])
                st.session_state[f"loaded_{setting_key}_idx"] = idx
            except ValueError:
                pass

    # Load sections directly
    if "sections" in loaded:
        st.session_state.sections = loaded["sections"]

    # Load lyrics content
    if "suno_lyrics" in loaded:
        st.session_state["loaded_lyrics"] = loaded["suno_lyrics"]

    # Load sidebar options
    if "use_llm" in loaded:
        st.session_state["loaded_use_llm"] = loaded["use_llm"]
    # ... etc
```

### Phase 2: Auto-Save Working Session

**File: `storage.py`**

Add new functions:

```python
WORKING_SESSION_FILE = Path(__file__).parent / "working_session.json"

def save_working_session(state: dict):
    """Save current working state for F5 recovery."""
    with open(WORKING_SESSION_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_working_session() -> dict | None:
    """Load working session if exists."""
    if WORKING_SESSION_FILE.exists():
        with open(WORKING_SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_working_session():
    """Clear working session file."""
    if WORKING_SESSION_FILE.exists():
        WORKING_SESSION_FILE.unlink()
```

**File: `app.py`**

Add auto-save trigger (at end of script, after all widgets rendered):

```python
# Auto-save working session
if st.session_state.get("_initialized", False):
    working_state = {
        "genre": selected_genre,
        "key": selected_key,
        "mode": selected_mode,
        # ... all widget values
        "sections": st.session_state.sections,
        "timestamp": datetime.now().isoformat()
    }
    save_working_session(working_state)
else:
    # First load - try to restore from working session
    saved = load_working_session()
    if saved:
        # Restore state...
        st.session_state["_initialized"] = True
        st.rerun()
    st.session_state["_initialized"] = True
```

---

## Additional UI Changes

**Sidebar - Add "New Session" button:**

```python
# In sidebar, after other controls
st.divider()
if st.button("🆕 New Session", use_container_width=True):
    clear_working_session()
    # Clear relevant session state
    for key in list(st.session_state.keys()):
        if not key.startswith("_"):
            del st.session_state[key]
    st.rerun()
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `app.py` | Enhanced save settings dict, enhanced load logic, auto-save trigger, New Session button |
| `storage.py` | New functions for working session save/load/clear |

---

## Verification

### Test 1: Enhanced Song Save
1. Configure all settings (genre, key, mode, etc.)
2. Add sections with instruments
3. Paste lyrics
4. Click Generate
5. Save song
6. Refresh browser (F5)
7. Load saved song
8. **Expected**: ALL settings restored, not just outputs

### Test 2: Auto-Save Recovery
1. Configure all settings
2. DO NOT save
3. Refresh browser (F5)
4. **Expected**: Settings automatically restored from working session

### Test 3: Fresh Start
1. Add "Clear Session" button or option
2. Click it
3. **Expected**: Working session cleared, fresh defaults shown
