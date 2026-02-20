# Phase 3: Developer Scenarios

## Goal

Add a scenario selector (visible only in Developer Focus mode) that applies a complete configuration - genre, mood, tempo, style preset, and song sections - with a single click. Users can still modify settings after applying a scenario.

## Documentation References

- [Phase 1: Profile Infrastructure](Phase1-ProfileInfrastructure.md) (prerequisite)
- [Phase 2: Developer Presets](Phase2-DeveloperPresets.md) (prerequisite)
- [Developer Focus Mode Spec - FR-4](../developer_focus_mode_spec.md)
- [Streamlit on_change Callbacks](https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox)

---

## Step 3.1: Scenario Selector UI

**File:** `app.py`

### Purpose

Add a scenario dropdown that appears only when Developer Focus is active. When a scenario is selected, an `on_change` callback applies all its configuration values to the app's session state.

### Implementation

Insert after the profile change tracking block, before Music Foundation (around line 420):

```python
# =============================================================================
# DEVELOPER SCENARIO + TECH CONTEXT (visible only in Developer Focus)
# =============================================================================

if is_dev_focus:
    st.divider()
    st.subheader("🎯 Developer Scenario")
    st.caption("Quick-apply a complete configuration for your coding task")

    scenario_options = ["-- Select Scenario --"] + get_dev_scenario_names()

    def apply_scenario():
        choice = st.session_state.get("scenario_select")
        if choice and choice != "-- Select Scenario --":
            scenario = get_dev_scenario(choice)
            if scenario:
                # Apply genre
                if scenario.get("genre") and scenario["genre"] in GENRES:
                    st.session_state["loaded_genre_idx"] = GENRES.index(scenario["genre"])
                    for key in ["style_preset_select", "style_influence_select"]:
                        if key in st.session_state:
                            del st.session_state[key]

                # Apply mood and tempo
                if scenario.get("mood"):
                    st.session_state["mood_select"] = scenario["mood"]
                if scenario.get("tempo"):
                    st.session_state["tempo_select"] = scenario["tempo"]

                # Apply style preset
                if scenario.get("style_preset"):
                    st.session_state["style_preset_select"] = scenario["style_preset"]

                # Apply sections
                if scenario.get("sections"):
                    st.session_state.sections = [
                        create_section(s["type"], s.get("instruments", ""))
                        for s in scenario["sections"]
                    ]

                # Reset the selectbox
                st.session_state["scenario_select"] = "-- Select Scenario --"

    col_scenario, col_desc = st.columns([1, 2])
    with col_scenario:
        st.selectbox(
            "Coding Scenario",
            options=scenario_options,
            key="scenario_select",
            on_change=apply_scenario
        )
    with col_desc:
        current_scenario = st.session_state.get("scenario_select", "-- Select Scenario --")
        if current_scenario != "-- Select Scenario --":
            scenario_data = get_dev_scenario(current_scenario)
            if scenario_data:
                st.info(f"_{scenario_data.get('description', '')}_")
```

### Key Concepts

1. **`on_change` callback** - `apply_scenario()` fires before the page re-renders. It reads the new selectbox value from `st.session_state["scenario_select"]` and applies all scenario fields.
2. **`create_section()` reuse** - Uses the existing section factory function to create sections with unique IDs, ensuring drag-and-drop compatibility.
3. **Reset after apply** - Sets `scenario_select` back to `"-- Select Scenario --"` so the same scenario can be re-applied later.
4. **Genre uses `loaded_genre_idx`** - Same pattern as profile change tracking. The `genre_select` widget key deletion ensures the index is respected on rerun.
5. **10 scenarios available** - Deep Debugging Session, Refactoring Legacy Code, Architecture Planning, Long Compilation/Training Wait, Data Analysis Flow, UI/UX Design Work, Documentation Writing, Code Review Session, Late Night Coding, Morning Focus Ramp-Up.

---

## Step 3.2: Dynamic Section Types

**File:** `app.py`

### Purpose

If a scenario introduces a section type not in the standard `SECTION_TYPES` list, the section type selectbox should still show it. Build an `effective_section_types` list dynamically.

### Implementation

In the section edit loop (around line 795):

```python
    with col_type:
        # Build effective section types (standard + any custom from current sections)
        effective_section_types = list(SECTION_TYPES)
        for s in st.session_state.sections:
            if s["type"] not in effective_section_types:
                effective_section_types.append(s["type"])
        new_type = st.selectbox(
            f"Section {i+1}",
            options=effective_section_types,
            index=effective_section_types.index(section["type"]) if section["type"] in effective_section_types else 0,
            key=f"section_type_{section_id}",
            label_visibility="collapsed"
        )
```

### Key Concepts

1. **Forward-compatible** - If future scenarios or user-created sections use non-standard types, they'll appear in the dropdown automatically
2. **Standard types always first** - The 12 standard Suno section types are listed first, custom types appended at the end
3. **Safe index lookup** - Falls back to index 0 if a type somehow isn't in the list

---

## Verification Checklist

- [ ] Scenario selector visible only when Developer Focus is active
- [ ] All 10 scenarios appear in the dropdown
- [ ] Selecting "Deep Debugging Session" sets: Genre=Ambient, Mood=Focused, Tempo=Slow, Preset=Debug Mode - Dark Ambient, 6 sections
- [ ] Selecting "Long Compilation/Training Wait" sets: Genre=Lo-fi, Mood=Relaxed, Preset=Compilation Wait - Lo-fi
- [ ] Sections update with correct types and instruments from the scenario
- [ ] User can modify settings after applying a scenario (fields are not locked)
- [ ] Scenario selector resets to "-- Select Scenario --" after apply
- [ ] Switching to General Purpose hides the scenario selector

## Next Phase

[Phase 4: Tech Context & Banner](Phase4-TechContextBanner.md)
