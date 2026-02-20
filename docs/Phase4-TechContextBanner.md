# Phase 4: Tech Context & Visual Banner

## Goal

Add a visual purple gradient banner when Developer Focus is active, a tech stack context input (project description + technology tags), and wire the context into the LLM generation pipeline.

## Documentation References

- [Phase 1: Profile Infrastructure](Phase1-ProfileInfrastructure.md) (prerequisite)
- [Phase 2: Developer Presets](Phase2-DeveloperPresets.md) (prerequisite)
- [Developer Focus Mode Spec - FR-5, FR-6](../developer_focus_mode_spec.md)

---

## Step 4.1: Visual Banner

**File:** `app.py`

### Purpose

A purple gradient banner (spec FR-6) appears immediately below the profile selector when Developer Focus is active. It communicates the mode's purpose at a glance.

### Implementation

Right after `is_dev_focus = selected_profile == "Developer Focus"` (around line 67):

```python
# Visual banner for Developer Focus mode (FR-6)
if is_dev_focus:
    st.markdown(
        """<div style="
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 8px 16px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            margin-bottom: 16px;
        "><strong>💻 Developer Focus Mode Active</strong><br/>
        <small>Optimized for: No/minimal vocals · Deep focus · 60-80 BPM range · Ambient/Minimal genres · Sustained concentration</small>
        </div>""",
        unsafe_allow_html=True,
    )
```

### Key Concepts

1. **`unsafe_allow_html=True`** - Required for inline CSS styling in Streamlit markdown
2. **Purple gradient** - `#667eea` to `#764ba2` matches the spec's developer/tech aesthetic
3. **Conditional render** - Only shown when `is_dev_focus` is True; disappears when switching back to General Purpose
4. **Summary text** - Tells the user exactly what this mode optimizes for, no need to read docs

---

## Step 4.2: Tech Stack Context UI

**File:** `app.py`

### Purpose

A text input and multiselect widget for describing the current coding task and selecting relevant technologies. This context can influence LLM-generated prompts and provides automatic track title suggestions.

### Implementation

Inside the `if is_dev_focus:` block, after the scenario selector (around line 474):

```python
    # Tech Stack Context (FR-5)
    st.subheader("🔧 Tech Stack Context")
    st.caption("Optional: describe what you're working on to influence generation")

    tech_context = st.text_input(
        "What are you working on?",
        placeholder="e.g., Refactoring legacy MFC code, Debugging PyTorch training, Building WPF UI",
        key="tech_stack_context",
        help="Describe your current task for contextual track titles"
    )

    selected_tech_tags = st.multiselect(
        "Tech Stack Tags",
        options=TECH_STACK_TAGS,
        default=[],
        key="tech_stack_tags",
        help="Select relevant technologies to add context"
    )

    # Generate suggested title from context
    if tech_context or selected_tech_tags:
        suggested_title = ""
        if tech_context:
            suggested_title = f"Focus Flow - {tech_context}"
        elif selected_tech_tags:
            suggested_title = f"Code Session - {' + '.join(selected_tech_tags[:2])}"
        if suggested_title:
            st.caption(f"💡 **Suggested Track Title:** {suggested_title}")
            st.session_state["suggested_title"] = suggested_title
```

### Key Concepts

1. **32 tech stack tags** - Organized by category: Languages, Frameworks, Domains, Tools, Activities
2. **Suggested title generation** - Automatic from context or first 2 tags; stored in session for the Save Song section
3. **Widget keys** - `tech_stack_context` and `tech_stack_tags` are cleared when switching away from Developer Focus (handled in Phase 1 change tracking)
4. **Both fields optional** - Users can generate without any tech context

---

## Step 4.3: Pass Tech Context to LLM Generation

**File:** `generator.py`

### Purpose

When generating via LLM mode, include the tech context as a subtle hint in the prompt message so the AI can adjust mood/language to match the developer's task.

### Implementation

In `_build_universal_llm_message()` (around line 550):

```python
    if selections.get("tech_context"):
        parts.append(f"Context: This is background music for a developer working on: {selections['tech_context']}. "
                     "Subtly adjust the mood to match this creative context.")
```

### Key Concepts

1. **Subtle influence, not override** - The prompt says "subtly adjust" to avoid the AI completely changing the requested genre/mood
2. **Only in LLM mode** - Static generation ignores tech context (the template-based approach doesn't use it)
3. **Already in `selections` dict** - `tech_context` was added to the selections in Phase 2 Step 2.5

---

## Step 4.4: Save/Restore Tech Context

**File:** `app.py`

### Purpose

Persist tech context and tags in the working session auto-save so they survive page reloads.

### Implementation

**Working session auto-save** (at bottom of `app.py`):

```python
_working_state = {
    # ... existing keys ...

    # Profile
    "profile": selected_profile,
    "tech_stack_context": st.session_state.get("tech_stack_context", ""),
    "tech_stack_tags": st.session_state.get("tech_stack_tags", []),
}
```

**Session restore** (in the `if "_session_loaded" not in st.session_state` block):

```python
        # Restore developer context
        if "tech_stack_context" in working:
            st.session_state["tech_stack_context"] = working["tech_stack_context"]
        if "tech_stack_tags" in working:
            st.session_state["tech_stack_tags"] = working["tech_stack_tags"]
```

### Key Concepts

1. **Auto-save on every render** - `save_working_session(_working_state)` runs at the bottom of every script execution, so tech context is always persisted
2. **Restore before widgets** - Session restore runs before the tech context widgets are instantiated, so `st.session_state` values are picked up automatically

---

## Verification Checklist

- [ ] Purple gradient banner appears when Developer Focus is selected
- [ ] Banner disappears when switching to General Purpose
- [ ] Banner text reads: "Developer Focus Mode Active / Optimized for: No/minimal vocals..."
- [ ] "What are you working on?" text input appears with placeholder
- [ ] Tech Stack Tags multiselect shows 32 options across 5 categories
- [ ] Typing a project description shows a suggested track title
- [ ] Selecting 2+ tech tags shows a suggested track title
- [ ] Generate in LLM mode with tech context produces output influenced by the context
- [ ] Generate in static mode works without errors (tech context silently ignored)
- [ ] Page reload restores tech context and tags
- [ ] Switching away from Developer Focus clears tech context

---

## Full Feature Summary

After completing all 4 phases, the Developer Focus Mode provides:

| Feature | Spec Reference | Implementation |
|---------|---------------|---------------|
| Profile selector | FR-1 | `st.selectbox` with 5 profiles, 2 active |
| Auto-populate defaults | FR-2 | Profile change tracking + `DEV_FOCUS_DEFAULTS` |
| 8 style presets | FR-3 | `DEV_STYLE_PRESETS` dict, conditional dropdown source |
| 10 coding scenarios | FR-4 | `DEV_SCENARIOS` dict, `on_change` callback |
| Tech stack context | FR-5 | Text input + multiselect, passed to LLM |
| Visual banner | FR-6 | Purple gradient HTML/CSS |
| Session persistence | FR-7 | Working session auto-save + restore |

### Files Modified/Created

| File | Changes |
|------|---------|
| `profiles.py` | **NEW** - All profile data, presets, scenarios, tags |
| `data.py` | Added 4 moods (Calm, Focused, Relaxed, Creative) |
| `app.py` | Profile selector, banner, scenarios, tech context, preset override, persistence |
| `generator.py` | `profile`/`tech_context` params, dev preset lookup in static + LLM paths |
