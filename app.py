"""
Suno Prompt Studio - Unified Streamlit App.
Generate Style and Lyrics fields for Suno AI music generation.

Run with: streamlit run app.py
"""

import os
import streamlit as st
from streamlit_sortables import sort_items
from data import (
    GENRES, MAJOR_KEYS, MINOR_KEYS, MODES, TIME_SIGNATURES,
    TEMPO_RANGES, MOOD_VARIATIONS, SECTION_TYPES, DEFAULT_SECTIONS,
    STYLE_PRESETS, STYLE_INFLUENCES, PROGRESSION_TYPES,
    HARMONIC_RHYTHM, CHORD_EXTENSIONS, LYRIC_TEMPLATES, POETIC_METERS
)
from generator import (
    generate_outputs, validate_lyrics_format, validate_lyrics_with_llm,
    suggest_song_title, suggest_section_instruments
)
from refiner import run_refinement_agent
from storage import load_history, save_song, delete_song, export_history_csv

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Suno Prompt Studio",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 Suno Prompt Studio")
st.caption("Generate Style and Lyrics fields for Suno AI music generation")

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.header("Settings")

    # API Key input
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=os.environ.get("OPENAI_API_KEY", ""),
        type="password",
        help="Required for LLM generation and AI refinement. Set OPENAI_API_KEY env var to pre-fill."
    )
    st.session_state["openai_api_key"] = api_key_input

    st.divider()

    # Generation mode
    st.subheader("Generation Mode")
    use_llm = st.toggle(
        "Use LLM Generation (Jazz only)",
        value=False,
        help="Use AI to generate coherent jazz prompts. Requires API key."
    )

    # Replace guitar stem option
    replace_guitar = st.checkbox(
        "Replace Guitar Stem",
        value=False,
        help="Force guitar as sole melodic voice (for replacing guitar track later)"
    )

    # Auto-fill sections toggle
    auto_fill_sections = st.checkbox(
        "Auto-fill section instruments",
        value=True,
        help="Automatically suggest instruments when loading presets (uses AI if API key provided)"
    )

    st.divider()

    # Song History
    st.header("📁 Song History")
    history = load_history()
    if history:
        for i, song in enumerate(reversed(history)):
            idx = len(history) - 1 - i
            col_title, col_del = st.columns([4, 1])
            with col_title:
                if st.button(song.get("title", f"Song {idx+1}"), key=f"load_{idx}", use_container_width=True):
                    # Load song settings
                    settings = song.get("settings", {})
                    st.session_state["loaded_song"] = settings
                    st.session_state["loaded_style"] = song.get("style_output", song.get("prompt", ""))
                    st.session_state["loaded_lyrics"] = song.get("lyrics_output", song.get("lyrics", ""))
                    st.rerun()
            with col_del:
                if st.button("✕", key=f"del_hist_{idx}"):
                    delete_song(idx)
                    st.rerun()

        # Export CSV
        csv_data = export_history_csv()
        if csv_data:
            st.download_button(
                "📤 Export CSV",
                csv_data,
                "suno_history.csv",
                "text/csv",
                use_container_width=True
            )
    else:
        st.caption("No saved songs yet")

    st.divider()

    st.header("About")
    st.markdown("""
    This tool generates **two outputs** for Suno:

    1. **Style Field**: Audio quality / style prompt
    2. **Lyrics Field**: Meta tags + structure + lyrics

    ### How to use:
    1. Select your genre and music settings
    2. Build your song structure with sections
    3. Optionally paste Suno lyrics or use a template
    4. Click Generate
    5. (Optional) Click Refine to improve with AI
    6. Copy each output to Suno
    """)

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================

# Section ID counter for unique identification
if "section_id_counter" not in st.session_state:
    st.session_state.section_id_counter = 0

def create_section(section_type: str, instruments: str = "") -> dict:
    """Create a new section with a unique ID."""
    st.session_state.section_id_counter += 1
    return {
        "id": st.session_state.section_id_counter,
        "type": section_type,
        "instruments": instruments
    }

if "sections" not in st.session_state:
    st.session_state.sections = [
        create_section("Intro", "ambient pads, soft piano"),
        create_section("Verse", "acoustic guitar, mellow tone"),
        create_section("Chorus", "full band, high energy"),
        create_section("Bridge", "synth arpeggios, rising tension"),
        create_section("Outro", "fade out, ambient"),
    ]
else:
    # Ensure all sections have IDs (migration for existing sessions)
    for section in st.session_state.sections:
        if "id" not in section:
            st.session_state.section_id_counter += 1
            section["id"] = st.session_state.section_id_counter

# Load song if selected from history
if "loaded_song" in st.session_state:
    loaded = st.session_state.pop("loaded_song")
    # Set session state values that will be picked up by widgets
    for key, value in loaded.items():
        st.session_state[f"loaded_{key}"] = value

# =============================================================================
# MUSIC FOUNDATION
# =============================================================================

st.header("🎹 Music Foundation")

col1, col2, col3 = st.columns(3)

with col1:
    selected_genre = st.selectbox(
        "Genre",
        options=GENRES,
        index=st.session_state.get("loaded_genre_idx", 0),
        help="Primary genre - Jazz enables jazz-specific options"
    )
    is_jazz = selected_genre == "Jazz"

with col2:
    # Key selection (combined major/minor)
    all_keys = {"None": ""} | MAJOR_KEYS | MINOR_KEYS
    selected_key = st.selectbox(
        "Key",
        options=list(all_keys.keys()),
        index=0,
        help="The tonal center of your song"
    )
    if selected_key != "None":
        st.caption(f"_{all_keys[selected_key]}_")

with col3:
    selected_mode = st.selectbox(
        "Mode",
        options=list(MODES.keys()),
        index=0,
        help="Modal flavor that affects emotional color"
    )
    mode_info = MODES[selected_mode]
    st.caption(f"_{mode_info['mood']}_")

col4, col5, col6 = st.columns(3)

with col4:
    selected_time_sig = st.selectbox(
        "Time Signature",
        options=list(TIME_SIGNATURES.keys()),
        index=0,
        help="Beat grouping that defines the groove"
    )
    st.caption(f"_{TIME_SIGNATURES[selected_time_sig]}_")

with col5:
    selected_tempo = st.selectbox(
        "Tempo",
        options=list(TEMPO_RANGES.keys()),
        index=2,  # Default to Mid-tempo
        help="Speed and energy of the song"
    )
    if selected_tempo != "None":
        st.caption(f"_{TEMPO_RANGES[selected_tempo]}_")

with col6:
    selected_mood = st.selectbox(
        "Mood",
        options=list(MOOD_VARIATIONS.keys()),
        index=0,
        help="Overall atmosphere and feel"
    )
    if selected_mood != "None":
        st.caption(f"_{MOOD_VARIATIONS[selected_mood]}_")

# =============================================================================
# JAZZ OPTIONS (Conditional)
# =============================================================================

if is_jazz:
    st.divider()
    st.header("🎸 Jazz Options")

    col_j1, col_j2 = st.columns(2)

    with col_j1:
        selected_preset = st.selectbox(
            "Style Preset",
            options=list(STYLE_PRESETS.keys()),
            index=0,
            help="Base jazz style template"
        )

    with col_j2:
        selected_influence = st.selectbox(
            "Style Influence",
            options=list(STYLE_INFLUENCES.keys()),
            index=0,
            help="Era or style influence to blend in"
        )

    # Harmony options
    st.subheader("🎼 Harmony")
    col_h1, col_h2, col_h3 = st.columns(3)

    with col_h1:
        selected_progression = st.selectbox(
            "Chord Progression",
            options=list(PROGRESSION_TYPES.keys()),
            index=0,
            help="Type of chord movement"
        )

    with col_h2:
        selected_harmonic_rhythm = st.selectbox(
            "Harmonic Rhythm",
            options=list(HARMONIC_RHYTHM.keys()),
            index=0,
            help="How often chords change"
        )

    with col_h3:
        selected_extensions = st.selectbox(
            "Chord Extensions",
            options=list(CHORD_EXTENSIONS.keys()),
            index=0,
            help="Chord voicing complexity"
        )
else:
    # Set defaults for non-jazz
    selected_preset = "Smooth Jazz"
    selected_influence = "None"
    selected_progression = "None"
    selected_harmonic_rhythm = "None"
    selected_extensions = "None"

# =============================================================================
# SONG STRUCTURE
# =============================================================================

st.divider()
st.header("📝 Song Structure (Meta Tags)")
st.caption("Define your song sections with instrument/mood descriptors")

# Add section button and preset selector
col_add, col_preset = st.columns([1, 2])

with col_add:
    if st.button("+ Add Section"):
        st.session_state.sections.append(create_section("Verse", ""))
        st.rerun()

with col_preset:
    preset_options = ["-- Select Preset --"] + list(DEFAULT_SECTIONS.keys())

    def apply_preset():
        choice = st.session_state.get("preset_select")
        if choice and choice != "-- Select Preset --":
            preset_sections = DEFAULT_SECTIONS.get(choice, DEFAULT_SECTIONS["default"])

            # Create sections
            new_sections = [create_section(s, "") for s in preset_sections]

            # Auto-fill if enabled - store for processing after widgets load
            st.session_state["_pending_autofill"] = True
            st.session_state.sections = new_sections

            # Reset the selectbox
            st.session_state["preset_select"] = "-- Select Preset --"

    st.selectbox(
        "Load preset structure",
        options=preset_options,
        key="preset_select",
        on_change=apply_preset
    )

# Handle pending auto-fill (after all selections are available)
if st.session_state.get("_pending_autofill") and auto_fill_sections:
    st.session_state.pop("_pending_autofill", None)
    api_key = st.session_state.get("openai_api_key", "")

    # Get current selections for auto-fill context
    filled_sections = suggest_section_instruments(
        sections=st.session_state.sections,
        genre=selected_genre,
        mood=selected_mood,
        key=selected_key if selected_key != "None" else None,
        mode=selected_mode,
        tempo=selected_tempo if selected_tempo != "None" else None,
        time_sig=selected_time_sig,
        style_preset=selected_preset if is_jazz else None,
        style_influence=selected_influence if is_jazz else None,
        progression=PROGRESSION_TYPES.get(selected_progression) if is_jazz and selected_progression != "None" else None,
        api_key=api_key if api_key else None
    )
    st.session_state.sections = filled_sections
    st.rerun()
elif st.session_state.get("_pending_autofill"):
    # Auto-fill disabled, clear flag
    st.session_state.pop("_pending_autofill", None)

# Create sortable items using unique ID - format: "id|Type: instruments"
sortable_items = [
    f"{s['id']}|{s['type']}: {s.get('instruments', '') or '(no instruments)'}"
    for s in st.session_state.sections
]

# Build ID to section mapping
id_to_section = {s['id']: s for s in st.session_state.sections}

# Display sortable list (drag and drop)
st.caption("Drag to reorder sections:")
sorted_items = sort_items(sortable_items, direction="vertical")

# Check if order changed by comparing IDs
sorted_ids = [int(item.split("|")[0]) for item in sorted_items]
current_ids = [s['id'] for s in st.session_state.sections]

if sorted_ids != current_ids:
    # Reorder sections based on drag result using ID mapping
    st.session_state.sections = [id_to_section[sid] for sid in sorted_ids]
    st.rerun()

# Display editable sections
st.caption("Edit sections:")
sections_to_remove = []

for i, section in enumerate(st.session_state.sections):
    section_id = section['id']
    col_num, col_type, col_instr, col_del = st.columns([0.3, 1, 3, 0.2])

    with col_num:
        st.markdown(f"**{i+1}.**")

    with col_type:
        new_type = st.selectbox(
            f"Section {i+1}",
            options=SECTION_TYPES,
            index=SECTION_TYPES.index(section["type"]) if section["type"] in SECTION_TYPES else 0,
            key=f"section_type_{section_id}",
            label_visibility="collapsed"
        )
        st.session_state.sections[i]["type"] = new_type

    with col_instr:
        new_instr = st.text_input(
            f"Instruments {i+1}",
            value=section.get("instruments", ""),
            key=f"section_instr_{section_id}",
            placeholder="e.g., acoustic guitar, mellow tone",
            label_visibility="collapsed"
        )
        st.session_state.sections[i]["instruments"] = new_instr

    with col_del:
        if st.button("✕", key=f"del_{section_id}", help="Remove section"):
            sections_to_remove.append(i)

# Remove marked sections
if sections_to_remove:
    for i in sorted(sections_to_remove, reverse=True):
        st.session_state.sections.pop(i)
    st.rerun()

# =============================================================================
# LYRICS
# =============================================================================

st.divider()
st.header("🎤 Lyrics")

col_template, col_paste = st.columns(2)

with col_template:
    selected_lyric_template = st.selectbox(
        "Lyric Template",
        options=list(LYRIC_TEMPLATES.keys()),
        index=0,
        help="Structured lyric template (overridden by pasted lyrics)"
    )

with col_paste:
    st.caption("Or paste Suno-generated lyrics:")

suno_lyrics = st.text_area(
    "Paste Suno Lyrics",
    height=150,
    placeholder="Paste lyrics from Suno here...\nThese will be included after the structure tags and take precedence over templates.",
    label_visibility="collapsed",
    value=st.session_state.get("loaded_lyrics", "")
)

# Poetic meter reference
with st.expander("📚 Poetic Meter Reference"):
    for meter_name, meter_info in POETIC_METERS.items():
        st.markdown(f"**{meter_name}**")
        st.caption(f"Pattern: {meter_info['pattern']} | Feel: {meter_info['feel']}")
        st.caption(f"Example: _{meter_info['example']}_")
        st.caption(f"Best for: {meter_info['genres']}")
        st.markdown("---")

# =============================================================================
# GENERATE
# =============================================================================

st.divider()

col_gen, col_batch = st.columns(2)

with col_gen:
    generate_clicked = st.button("🎵 Generate", type="primary", use_container_width=True)

with col_batch:
    batch_count = st.number_input("Batch count", min_value=1, max_value=5, value=1, label_visibility="collapsed")
    batch_clicked = st.button("📦 Batch Generate", use_container_width=True)

if generate_clicked or batch_clicked:
    api_key = st.session_state.get("openai_api_key", "")

    # Check if LLM is enabled but no API key
    if use_llm and is_jazz and not api_key:
        st.error("OpenAI API key required for LLM generation. Add it in the sidebar or disable LLM mode.")
    else:
        count = batch_count if batch_clicked else 1

        for batch_idx in range(count):
            with st.spinner(f"Generating{f' ({batch_idx+1}/{count})' if count > 1 else ''}..."):
                try:
                    result = generate_outputs(
                        genre=selected_genre,
                        key=selected_key if selected_key != "None" else "",
                        mode=selected_mode,
                        tempo=selected_tempo if selected_tempo != "None" else "",
                        time_sig=selected_time_sig,
                        mood=MOOD_VARIATIONS.get(selected_mood, ""),
                        sections=st.session_state.sections,
                        suno_lyrics=suno_lyrics,
                        lyric_template=selected_lyric_template,
                        style_preset=selected_preset,
                        style_influence=selected_influence,
                        progression=PROGRESSION_TYPES.get(selected_progression, ""),
                        harmonic_rhythm=HARMONIC_RHYTHM.get(selected_harmonic_rhythm, ""),
                        extensions=CHORD_EXTENSIONS.get(selected_extensions, ""),
                        replace_guitar=replace_guitar,
                        use_llm=use_llm and is_jazz,
                        api_key=api_key if (use_llm and is_jazz) else None
                    )

                    # Store in session state
                    if batch_idx == 0:
                        st.session_state.generated_style = result["style"]
                        st.session_state.generated_lyrics = result["lyrics"]
                        st.session_state.was_cached = result.get("cached", False)
                    else:
                        # For batch, append to list
                        if "batch_results" not in st.session_state:
                            st.session_state.batch_results = []
                        st.session_state.batch_results.append(result)

                except Exception as e:
                    st.error(f"Generation failed: {e}")

# =============================================================================
# DISPLAY OUTPUTS
# =============================================================================

if "generated_style" in st.session_state:
    st.header("📋 Generated Outputs")

    if st.session_state.get("was_cached"):
        st.info("💾 Loaded from cache")

    col_style, col_lyrics = st.columns(2)

    with col_style:
        st.subheader("Style Field")
        st.caption("Paste into Suno's **Style** box")
        st.text_area(
            "Style output",
            value=st.session_state.generated_style,
            height=400,
            key="style_output_display",
            label_visibility="collapsed"
        )

    with col_lyrics:
        st.subheader("Lyrics Field")
        st.caption("Paste into Suno's **Lyrics** box")
        st.text_area(
            "Lyrics output",
            value=st.session_state.generated_lyrics,
            height=400,
            key="lyrics_output_display",
            label_visibility="collapsed"
        )

    # Show batch results if any
    if "batch_results" in st.session_state and st.session_state.batch_results:
        st.subheader("📦 Batch Results")
        for i, result in enumerate(st.session_state.batch_results, start=2):
            with st.expander(f"Variation {i}"):
                col_bs, col_bl = st.columns(2)
                with col_bs:
                    st.text_area(f"Style {i}", value=result["style"], height=200, label_visibility="collapsed")
                with col_bl:
                    st.text_area(f"Lyrics {i}", value=result["lyrics"], height=200, label_visibility="collapsed")

    # =============================================================================
    # LYRICS VALIDATION
    # =============================================================================

    st.divider()
    st.subheader("🔍 Lyrics Format Validation")

    # Get current lyrics (use refined if available, otherwise generated)
    lyrics_to_validate = st.session_state.get("refined_lyrics", st.session_state.generated_lyrics)

    # Local validation (always runs)
    local_validation = validate_lyrics_format(lyrics_to_validate)

    # Display local validation results
    if local_validation["warnings"]:
        for warning in local_validation["warnings"]:
            st.warning(warning)

    if local_validation["suggestions"]:
        with st.expander("💡 Suggestions", expanded=len(local_validation["warnings"]) > 0):
            for suggestion in local_validation["suggestions"]:
                st.info(f"💡 {suggestion}")

    # Tag analysis
    tag_analysis = local_validation.get("tag_analysis", {})
    if tag_analysis.get("total_tags", 0) > 0:
        with st.expander("📊 Tag Analysis"):
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("Total Tags", tag_analysis["total_tags"])
            with col_t2:
                st.metric("Standard Tags", tag_analysis["standard_tags"])
            with col_t3:
                custom_count = tag_analysis["custom_tags"]
                st.metric("Custom Tags", custom_count, delta="⚠️" if custom_count > 0 else None)

            if tag_analysis.get("tag_counts"):
                st.caption("Tag frequency:")
                st.json(tag_analysis["tag_counts"])

    # AI validation (optional)
    api_key = st.session_state.get("openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")

    if api_key:
        col_validate, col_fix = st.columns(2)

        with col_validate:
            if st.button("🤖 Validate with AI", use_container_width=True):
                with st.spinner("AI is analyzing lyrics format..."):
                    ai_result = validate_lyrics_with_llm(lyrics_to_validate, api_key)
                    st.session_state.ai_validation = ai_result

        with col_fix:
            if st.session_state.get("ai_validation", {}).get("corrected_lyrics"):
                if st.button("✅ Apply AI Corrections", use_container_width=True):
                    corrected = st.session_state.ai_validation["corrected_lyrics"]
                    st.session_state.generated_lyrics = corrected
                    if "refined_lyrics" in st.session_state:
                        st.session_state.refined_lyrics = corrected
                    st.success("Applied AI corrections!")
                    st.rerun()

        # Display AI validation results
        if "ai_validation" in st.session_state:
            ai_result = st.session_state.ai_validation

            if ai_result.get("valid"):
                st.success("✅ AI validation passed - lyrics format looks good!")
            else:
                if ai_result.get("issues"):
                    st.error("❌ AI found issues:")
                    for issue in ai_result["issues"]:
                        st.markdown(f"- {issue}")

                if ai_result.get("suggestions"):
                    st.info("💡 AI suggestions:")
                    for suggestion in ai_result["suggestions"]:
                        st.markdown(f"- {suggestion}")

                if ai_result.get("corrected_lyrics"):
                    with st.expander("📝 AI-Corrected Version"):
                        st.text_area(
                            "Corrected lyrics",
                            value=ai_result["corrected_lyrics"],
                            height=300,
                            label_visibility="collapsed",
                            key="ai_corrected_preview"
                        )
    else:
        st.caption("💡 Add OpenAI API key in sidebar for AI-powered format validation")

    if local_validation["valid"] and not local_validation["warnings"]:
        st.success("✅ Local validation passed - no obvious format issues detected")

    # =============================================================================
    # REFINER
    # =============================================================================

    st.divider()
    st.subheader("🔧 Refine with AI")
    st.caption("Use OpenAI to analyze and improve both outputs")

    api_key = st.session_state.get("openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")

    if api_key:
        if st.button("✨ Refine Outputs", type="secondary", use_container_width=True):
            with st.spinner("Analyzing and refining outputs..."):
                try:
                    result = run_refinement_agent(
                        st.session_state.generated_style,
                        st.session_state.generated_lyrics,
                        api_key,
                        is_jazz=is_jazz
                    )
                    st.session_state.refined_style = result["refined_style"]
                    st.session_state.refined_lyrics = result["refined_lyrics"]
                    st.session_state.refiner_reasoning = result["reasoning"]
                    st.session_state.style_score = result["style_score"]
                    st.session_state.lyrics_score = result["lyrics_score"]
                except Exception as e:
                    st.error(f"Refinement failed: {e}")
    else:
        st.info("Enter OpenAI API key in the sidebar to enable refinement")

    # Display refined outputs
    if "refined_style" in st.session_state:
        st.markdown("---")
        st.markdown(f"**Scores:** Style {st.session_state.style_score}/10 | Lyrics {st.session_state.lyrics_score}/10")

        col_ref_style, col_ref_lyrics = st.columns(2)

        with col_ref_style:
            st.markdown("**Refined Style Field**")
            st.text_area(
                "Refined style",
                value=st.session_state.refined_style,
                height=400,
                key="refined_style_display",
                label_visibility="collapsed"
            )

        with col_ref_lyrics:
            st.markdown("**Refined Lyrics Field**")
            st.text_area(
                "Refined lyrics",
                value=st.session_state.refined_lyrics,
                height=400,
                key="refined_lyrics_display",
                label_visibility="collapsed"
            )

        # Show reasoning
        with st.expander("🔍 Refinement Reasoning"):
            for step in st.session_state.refiner_reasoning:
                if "action" in step:
                    st.markdown(f"**Action:** `{step['action']}`")
                if "observation" in step:
                    st.markdown(f"→ {step['observation']}")
                if "details" in step:
                    st.caption(step["details"])

    # =============================================================================
    # SAVE SONG
    # =============================================================================

    st.divider()
    st.subheader("💾 Save Song")

    col_title, col_suggest, col_save = st.columns([2.5, 0.5, 1])

    with col_title:
        # Use suggested title if available
        default_title = st.session_state.get("suggested_title", "")
        song_title = st.text_input(
            "Song Title",
            value=default_title,
            placeholder="Enter a title for this song...",
            label_visibility="collapsed"
        )

    with col_suggest:
        if st.button("💡", help="Suggest a title based on your settings", use_container_width=True):
            api_key = st.session_state.get("openai_api_key", "")
            suggested = suggest_song_title(
                genre=selected_genre,
                mood=selected_mood,
                key=selected_key,
                mode=selected_mode,
                use_llm=bool(api_key),
                api_key=api_key
            )
            st.session_state.suggested_title = suggested
            st.rerun()

    with col_save:
        if st.button("Save", use_container_width=True):
            if song_title:
                settings = {
                    "genre": selected_genre,
                    "key": selected_key,
                    "mode": selected_mode,
                    "tempo": selected_tempo,
                    "time_sig": selected_time_sig,
                    "mood": selected_mood,
                    "sections": st.session_state.sections,
                }
                if is_jazz:
                    settings.update({
                        "style_preset": selected_preset,
                        "style_influence": selected_influence,
                        "progression": selected_progression,
                        "harmonic_rhythm": selected_harmonic_rhythm,
                        "extensions": selected_extensions,
                    })

                # Use refined outputs if available
                style_to_save = st.session_state.get("refined_style", st.session_state.generated_style)
                lyrics_to_save = st.session_state.get("refined_lyrics", st.session_state.generated_lyrics)

                save_song(song_title, settings, style_to_save, lyrics_to_save)
                st.success(f"Saved: {song_title}")
                st.rerun()
            else:
                st.warning("Enter a title to save")
