# Phase 2: Developer Style Presets

## Goal

Make 8 developer-specific style presets (defined in `profiles.py`) appear in the Style Preset dropdown when Developer Focus is active, and handle them correctly in the generation pipeline (`generator.py`).

## Documentation References

- [Phase 1: Profile Infrastructure](Phase1-ProfileInfrastructure.md) (prerequisite)
- [Developer Focus Mode Spec - FR-3](../developer_focus_mode_spec.md)

---

## Step 2.1: Override Preset Source in `app.py`

**File:** `app.py`

### Purpose

The Style Preset dropdown normally shows genre-specific presets via `get_genre_preset_names(genre)`. When Developer Focus is active, it should instead show the 8 developer presets from `DEV_STYLE_PRESETS`.

### Implementation

In the Options section where the Style Preset selectbox is rendered (around line 620):

```python
with col_j1:
    # Dynamic Style Preset names based on genre (or developer presets)
    if is_dev_focus:
        preset_names = get_dev_preset_names()
    else:
        preset_names = get_genre_preset_names(selected_genre)
    selected_preset = st.selectbox(
        "Style Preset",
        options=list(preset_names.keys()),
        index=0,
        key="style_preset_select",
        help="Developer focus presets" if is_dev_focus else "Base style template adapted to your genre"
    )
    # Show preset description for developer presets
    if is_dev_focus and selected_preset != "None" and selected_preset in DEV_STYLE_PRESETS:
        st.caption(f"_{DEV_STYLE_PRESETS[selected_preset][:80]}..._")
```

### Key Concepts

1. **Conditional preset source** - `is_dev_focus` flag switches between `get_dev_preset_names()` and `get_genre_preset_names()`
2. **Same widget key** - The `style_preset_select` key is reused; the profile change tracking deletes it when switching profiles so the options list refreshes
3. **Preset description caption** - Developer presets show a truncated description below the dropdown so users see what they'll get
4. **Both return dicts** - `get_dev_preset_names()` and `get_genre_preset_names()` both return `dict[str, str]` so the selectbox `options=list(preset_names.keys())` pattern works for both

---

## Step 2.2: Add Profile Import to `generator.py`

**File:** `generator.py`

### Purpose

Import `DEV_STYLE_PRESETS` so the generator can resolve developer preset values.

### Implementation

Add after the existing data import (around line 18):

```python
from profiles import DEV_STYLE_PRESETS
```

### Key Concepts

1. **Only `DEV_STYLE_PRESETS` needed** - The generator doesn't need profiles, scenarios, or tech tags - only the preset name-to-value mapping

---

## Step 2.3: Add `profile` and `tech_context` Parameters to `generate_outputs()`

**File:** `generator.py`

### Purpose

Add two new parameters so the generation pipeline knows which profile is active and can receive tech context for LLM mode.

### Implementation

Update the `generate_outputs()` function signature:

```python
def generate_outputs(
    genre: str,
    key: str = "",
    mode: str = "",
    tempo: str = "",
    time_sig: str = "",
    mood: str = "",
    style_preset: str = "None",
    style_influence: str = "None",
    progression: str = "None",
    harmonic_rhythm: str = "None",
    extensions: str = "None",
    sections: list = None,
    lyrics_text: str = "",
    lyric_template: str = "None",
    replace_guitar: bool = False,
    use_llm: bool = False,
    api_key: str = None,
    # Profile
    profile: str = "General Purpose",
    tech_context: str = "",
) -> dict:
```

### Key Concepts

1. **Default values preserve backward compatibility** - Existing callers don't need to pass `profile` or `tech_context`
2. **Both parameters are strings** - Simple, no new types needed

---

## Step 2.4: Dev Preset Lookup in Static Generation

**File:** `generator.py`

### Purpose

When generating in static (non-LLM) mode, resolve developer preset names to their descriptive values. The existing `resolve_preset_value()` only knows about genre presets, so developer presets must be checked first.

### Implementation

In the universal static generation path (around line 235):

```python
            # Add style preset value (the musical description, not just the name)
            if style_preset and style_preset != "None":
                # Check developer presets first, then genre presets
                if profile == "Developer Focus" and style_preset in DEV_STYLE_PRESETS:
                    preset_value = DEV_STYLE_PRESETS[style_preset]
                else:
                    preset_value = resolve_preset_value(style_preset, genre)
                if preset_value:
                    style_parts.append(preset_value)
```

### Key Concepts

1. **Priority order** - Developer presets are checked first when `profile == "Developer Focus"`, falling through to genre presets otherwise
2. **Same output format** - Both developer and genre presets produce a string that gets appended to `style_parts`
3. **`resolve_preset_value()` would return empty** for developer preset names since they don't exist in `STYLE_PRESETS` - the guard prevents this

---

## Step 2.5: Dev Preset in LLM Generation

**File:** `generator.py`

### Purpose

When generating via LLM, resolve the developer preset name to include its description in the LLM context, so the model understands the intended sound.

### Implementation

In `_generate_universal_llm()` (around line 451):

```python
def _generate_universal_llm(
    genre, key, mode, tempo, time_sig, mood,
    style_preset, style_influence,
    progression, harmonic_rhythm, extensions,
    sections, api_key,
    tech_context: str = "",
    profile: str = "General Purpose",
) -> dict:
    """Generate prompt for any genre using LLM."""
    section_hints = _extract_section_style_hints(sections)

    # Resolve developer preset value if applicable
    resolved_preset = style_preset
    if profile == "Developer Focus" and style_preset in DEV_STYLE_PRESETS:
        resolved_preset = f"{style_preset} ({DEV_STYLE_PRESETS[style_preset]})"

    selections = {
        "genre": genre,
        "key_signature": key,
        "mode": mode,
        "tempo": tempo,
        "time_sig": time_sig,
        "mood": mood,
        "style_preset": resolved_preset,
        "style_influence": style_influence,
        "progression": progression,
        "harmonic_rhythm": harmonic_rhythm,
        "extensions": extensions,
        "section_hints": section_hints,
        "tech_context": tech_context,
    }
    # ... rest of function
```

### Key Concepts

1. **Resolved preset includes both name and value** - `"Debug Mode - Dark Ambient (deep bass drones, sparse industrial...)"` gives the LLM rich context
2. **`tech_context` passed through to `_build_universal_llm_message()`** - See Phase 4

---

## Step 2.6: Pass Profile from `app.py` Generate Call

**File:** `app.py`

### Purpose

Pass the selected profile and tech context to the generation function.

### Implementation

In the Generate button handler (around line 1063):

```python
                    result = generate_outputs(
                        genre=selected_genre,
                        # ... existing params ...
                        replace_guitar=replace_guitar,
                        use_llm=use_llm,
                        api_key=api_key if use_llm else None,
                        profile=selected_profile,
                        tech_context=st.session_state.get("tech_stack_context", "") if is_dev_focus else "",
                    )
```

### Key Concepts

1. **`tech_context` only sent when `is_dev_focus`** - Prevents stale context from leaking when profile is General Purpose
2. **`profile` always sent** - The generator uses the default `"General Purpose"` to skip dev preset logic

---

## Verification Checklist

- [ ] Developer Focus shows 8 presets: None, Deep Focus - Minimal, Deep Focus - Nature Ambient, Code Flow - Synthwave, Debug Mode - Dark Ambient, Compilation Wait - Lo-fi, Neural Network Training, Late Night Coding, Morning Ramp-Up
- [ ] Selecting a dev preset shows its description caption below the dropdown
- [ ] General Purpose shows the genre-specific presets as before
- [ ] Generate (static mode) with a dev preset produces style output containing the preset description
- [ ] Generate (LLM mode) with a dev preset works without errors
- [ ] Switching from Developer Focus to General Purpose refreshes the preset dropdown to genre presets

## Next Phase

[Phase 3: Developer Scenarios](Phase3-DeveloperScenarios.md)
