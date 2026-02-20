"""
Suno Prompt Studio — Main Streamlit Application.
Generates Style and Lyrics fields for Suno AI music generation.
Supports Jazz-specific features, universal genres, and Developer Focus mode.
"""

import uuid
import streamlit as st
from data import (
    GENRES, STYLE_PRESETS, STYLE_INFLUENCES,
    NOTE_NAMES, KEY_QUALITIES, MODES,
    TIME_SIGNATURES,
    TEMPO_VARIATIONS, MOOD_VARIATIONS, INTRO_VARIATIONS,
    PROGRESSION_TYPES, HARMONIC_RHYTHM, CHORD_EXTENSIONS,
    SECTION_TYPES, DEFAULT_SECTIONS, LYRIC_TEMPLATES,
    get_genre_preset_names, get_genre_influence_names,
    get_modes_for_quality, resolve_key_value,
)
from profiles import (
    PROFILES, ACTIVE_PROFILES, DEV_STYLE_PRESETS, DEV_SCENARIOS,
    TECH_STACK_TAGS,
    get_profile_defaults, get_dev_preset_names, get_dev_scenario_names, get_dev_scenario,
)
from generator import (
    generate_outputs, suggest_song_title,
    suggest_section_instruments, detect_section_conflicts,
    validate_lyrics_format, parse_lyrics_to_sections,
)
from refiner import run_refinement_agent
from iterative_refiner import generate_suggestions, apply_suggestions
from storage import (
    load_history, save_song, delete_song, export_history_csv,
    save_working_session, load_working_session,
)


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Suno Prompt Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Suno Prompt Studio")
st.caption("Generate Style and Lyrics fields for Suno AI")


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize session state with defaults, restoring from working session if available."""
    defaults = {
        "profile": "General Purpose",
        "genre": "Jazz",
        "key": "None",
        "key_quality": "Major",
        "mode": "Ionian (Major)",
        "tempo": "None",
        "time_sig": "4/4",
        "mood": "None",
        "style_preset": "Smooth Jazz",
        "style_influence": "None",
        "progression": "None",
        "harmonic_rhythm": "None",
        "extensions": "None",
        "lyric_template": "None",
        "suno_lyrics": "",
        "replace_guitar": False,
        "use_llm": False,
        "api_key": "",
        "tech_context": "",
        "dev_scenario": "None",
        "sections": [
            {"id": str(uuid.uuid4()), "type": "Intro", "instruments": ""},
            {"id": str(uuid.uuid4()), "type": "Verse", "instruments": ""},
            {"id": str(uuid.uuid4()), "type": "Chorus", "instruments": ""},
            {"id": str(uuid.uuid4()), "type": "Bridge", "instruments": ""},
            {"id": str(uuid.uuid4()), "type": "Outro", "instruments": ""},
        ],
        "style_output": "",
        "lyrics_output": "",
        "iter_versions": [],
        "iter_suggestions": [],
        "iter_active": False,
        "_initialized": False,
    }

    # Set defaults for missing keys
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Restore from working session on first load
    if not st.session_state._initialized:
        saved = load_working_session()
        if saved:
            for key, value in saved.items():
                if key in defaults and key != "_initialized":
                    st.session_state[key] = value
        st.session_state._initialized = True


init_session_state()


def save_current_session():
    """Save current state for F5 recovery."""
    state = {}
    save_keys = [
        "profile", "genre", "key", "key_quality", "mode", "tempo", "time_sig", "mood",
        "style_preset", "style_influence", "progression", "harmonic_rhythm",
        "extensions", "lyric_template", "suno_lyrics", "replace_guitar",
        "use_llm", "tech_context", "dev_scenario", "sections",
        "style_output", "lyrics_output",
    ]
    for k in save_keys:
        if k in st.session_state:
            state[k] = st.session_state[k]
    save_working_session(state)


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.header("Settings")

    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Required for LLM generation and AI refinement",
        key="w_api_key",
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key

    st.divider()

    # Generation Mode
    use_llm = st.checkbox(
        "LLM Generation",
        value=st.session_state.use_llm,
        help="Use AI for creative, coherent prompt generation (requires API key)",
        key="w_use_llm",
    )
    if use_llm != st.session_state.use_llm:
        st.session_state.use_llm = use_llm

    # Replace Guitar Stem
    replace_guitar = st.checkbox(
        "Replace Guitar Stem",
        value=st.session_state.replace_guitar,
        help="Ensures guitar is always the primary melodic voice for stem replacement",
        key="w_replace_guitar",
    )
    if replace_guitar != st.session_state.replace_guitar:
        st.session_state.replace_guitar = replace_guitar

    st.divider()

    # Song History
    st.subheader("Song History")
    history = load_history()
    if history:
        for i, song in enumerate(reversed(history)):
            idx = len(history) - 1 - i
            with st.expander(f"{song.get('title', 'Untitled')} — {song.get('timestamp', '')[:10]}"):
                st.text(song.get("style_output", "")[:200] + "...")
                col_load, col_del = st.columns(2)
                if col_load.button("Load", key=f"load_{idx}"):
                    settings = song.get("settings", {})
                    for k, v in settings.items():
                        if k in st.session_state:
                            st.session_state[k] = v
                    st.session_state.style_output = song.get("style_output", "")
                    st.session_state.lyrics_output = song.get("lyrics_output", "")
                    st.rerun()
                if col_del.button("Delete", key=f"del_{idx}"):
                    delete_song(idx)
                    st.rerun()

        csv = export_history_csv()
        if csv:
            st.download_button("Export CSV", csv, "suno_history.csv", "text/csv")
    else:
        st.caption("No songs saved yet.")


# =============================================================================
# PROFILE SELECTOR
# =============================================================================

profile_options = PROFILES
profile_idx = profile_options.index(st.session_state.profile) if st.session_state.profile in profile_options else 0

profile = st.selectbox(
    "Profile",
    profile_options,
    index=profile_idx,
    format_func=lambda x: f"{x} (coming soon)" if x not in ACTIVE_PROFILES else x,
    key="w_profile",
)

# Handle profile change
if profile != st.session_state.profile:
    if profile in ACTIVE_PROFILES:
        st.session_state.profile = profile
        defaults = get_profile_defaults(profile)
        if defaults:
            for k, v in defaults.items():
                st.session_state[k] = v
        st.rerun()
    else:
        st.warning(f"{profile} is coming soon!")
        st.session_state.profile = st.session_state.profile  # revert


# =============================================================================
# DEVELOPER FOCUS MODE
# =============================================================================

is_dev_focus = st.session_state.profile == "Developer Focus"

if is_dev_focus:
    st.markdown(
        """<div style="background-color: #2d1b69; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
        <strong style="color: #b39ddb;">Developer Focus Mode</strong>
        <span style="color: #ce93d8;"> — Background music optimized for coding sessions</span>
        </div>""",
        unsafe_allow_html=True,
    )

    # Scenario selector
    scenario_names = ["None"] + get_dev_scenario_names()
    scenario_idx = scenario_names.index(st.session_state.dev_scenario) if st.session_state.dev_scenario in scenario_names else 0

    dev_scenario = st.selectbox(
        "Developer Scenario",
        scenario_names,
        index=scenario_idx,
        help="Pre-configured settings for specific coding activities",
        key="w_dev_scenario",
    )

    if dev_scenario != st.session_state.dev_scenario:
        st.session_state.dev_scenario = dev_scenario
        if dev_scenario != "None":
            scenario = get_dev_scenario(dev_scenario)
            if scenario:
                if "genre" in scenario:
                    st.session_state.genre = scenario["genre"]
                if "tempo" in scenario:
                    st.session_state.tempo = scenario["tempo"]
                if "mood" in scenario:
                    st.session_state.mood = scenario["mood"]
                if "style_preset" in scenario:
                    st.session_state.style_preset = scenario["style_preset"]
                if "sections" in scenario:
                    st.session_state.sections = [
                        {"id": str(uuid.uuid4()), "type": s["type"], "instruments": s.get("instruments", "")}
                        for s in scenario["sections"]
                    ]
                st.rerun()

    # Tech context
    tech_context = st.text_input(
        "Tech Context",
        value=st.session_state.tech_context,
        placeholder="e.g., Python, PyTorch, debugging ML pipeline",
        help="Subtly influences the mood when using LLM generation",
        key="w_tech_context",
    )
    if tech_context != st.session_state.tech_context:
        st.session_state.tech_context = tech_context

    # Tech stack tags
    with st.expander("Quick Tech Tags"):
        tag_cols = st.columns(6)
        for i, tag in enumerate(TECH_STACK_TAGS):
            col = tag_cols[i % 6]
            if col.button(tag, key=f"tag_{tag}", use_container_width=True):
                current = st.session_state.tech_context
                if tag not in current:
                    st.session_state.tech_context = (current + ", " + tag).strip(", ")
                    st.rerun()


# =============================================================================
# MUSIC FOUNDATION
# =============================================================================

st.header("Music Foundation")

is_jazz = st.session_state.genre == "Jazz"

col1, col2, col3 = st.columns(3)

with col1:
    genre_idx = GENRES.index(st.session_state.genre) if st.session_state.genre in GENRES else 0
    genre = st.selectbox("Genre", GENRES, index=genre_idx, key="w_genre")

    if genre != st.session_state.genre:
        st.session_state.genre = genre
        # Reset genre-specific options
        st.session_state.style_preset = "Smooth Jazz" if genre == "Jazz" else "None"
        st.session_state.style_influence = "None"
        st.rerun()

    # Key (note name)
    note_idx = NOTE_NAMES.index(st.session_state.key) if st.session_state.key in NOTE_NAMES else 0
    key = st.selectbox("Key", NOTE_NAMES, index=note_idx, key="w_key")
    if key != st.session_state.key:
        st.session_state.key = key

    # Key Quality (Major / Minor / Minor Maj7)
    q_idx = KEY_QUALITIES.index(st.session_state.key_quality) if st.session_state.key_quality in KEY_QUALITIES else 0
    quality = st.selectbox("Quality", KEY_QUALITIES, index=q_idx, key="w_key_quality")
    if quality != st.session_state.key_quality:
        st.session_state.key_quality = quality
        # Reset mode when quality changes
        st.session_state.mode = "None"
        st.rerun()

with col2:
    # Mode — filtered by key quality, disabled for Minor Maj7
    available_modes = get_modes_for_quality(st.session_state.key_quality)
    mode_names = list(available_modes.keys()) if available_modes else []

    if not mode_names:
        # Minor Maj7 — no mode selection
        st.selectbox("Mode", ["(fixed by quality)"], disabled=True, key="w_mode_disabled")
        if st.session_state.mode != "None":
            st.session_state.mode = "None"
    else:
        mode_idx = mode_names.index(st.session_state.mode) if st.session_state.mode in mode_names else 0
        mode = st.selectbox("Mode", mode_names, index=mode_idx, key="w_mode")
        if mode != st.session_state.mode:
            st.session_state.mode = mode

    # Tempo
    if is_jazz:
        tempo_names = list(TEMPO_VARIATIONS.keys())
    else:
        tempo_names = ["None", "Slow (60-80 BPM)", "Mid-tempo (80-110 BPM)",
                       "Uptempo (110-130 BPM)", "Fast (130+ BPM)"]
    tempo_idx = tempo_names.index(st.session_state.tempo) if st.session_state.tempo in tempo_names else 0
    tempo = st.selectbox("Tempo", tempo_names, index=tempo_idx, key="w_tempo")
    if tempo != st.session_state.tempo:
        st.session_state.tempo = tempo

with col3:
    # Time Signature
    ts_idx = TIME_SIGNATURES.index(st.session_state.time_sig) if st.session_state.time_sig in TIME_SIGNATURES else 0
    time_sig = st.selectbox("Time Signature", TIME_SIGNATURES, index=ts_idx, key="w_time_sig")
    if time_sig != st.session_state.time_sig:
        st.session_state.time_sig = time_sig

    # Mood
    mood_names = list(MOOD_VARIATIONS.keys())
    mood_idx = mood_names.index(st.session_state.mood) if st.session_state.mood in mood_names else 0
    mood = st.selectbox("Mood", mood_names, index=mood_idx, key="w_mood")
    if mood != st.session_state.mood:
        st.session_state.mood = mood


# =============================================================================
# STYLE OPTIONS
# =============================================================================

st.header("Style Options")

opt_col1, opt_col2 = st.columns(2)

with opt_col1:
    # Style Preset (genre-specific or developer-specific)
    if is_dev_focus:
        preset_dict = get_dev_preset_names()
    else:
        preset_dict = get_genre_preset_names(st.session_state.genre)

    preset_names = list(preset_dict.keys())
    preset_idx = preset_names.index(st.session_state.style_preset) if st.session_state.style_preset in preset_names else 0
    style_preset = st.selectbox(
        "Style Preset",
        preset_names,
        index=preset_idx,
        help="Prescriptive style foundation — detailed instrument roles and tones",
        key="w_style_preset",
    )
    if style_preset != st.session_state.style_preset:
        st.session_state.style_preset = style_preset

    # Show preset preview
    if style_preset and style_preset != "None":
        preview = preset_dict.get(style_preset, "")
        if preview:
            st.caption(f"Preview: {preview[:120]}...")

with opt_col2:
    # Style Influence
    influence_dict = get_genre_influence_names(st.session_state.genre)
    influence_names = list(influence_dict.keys())
    influence_idx = influence_names.index(st.session_state.style_influence) if st.session_state.style_influence in influence_names else 0
    style_influence = st.selectbox(
        "Style Influence",
        influence_names,
        index=influence_idx,
        help="Era/style reference that colors the output",
        key="w_style_influence",
    )
    if style_influence != st.session_state.style_influence:
        st.session_state.style_influence = style_influence


# Jazz/Harmony options (shown for Jazz and optionally for other genres)
if is_jazz or st.session_state.genre in ["Classical", "Blues", "Soul", "Funk", "R&B"]:
    st.subheader("Harmony Options")
    harm_col1, harm_col2, harm_col3 = st.columns(3)

    with harm_col1:
        prog_names = list(PROGRESSION_TYPES.keys())
        prog_idx = prog_names.index(st.session_state.progression) if st.session_state.progression in prog_names else 0
        progression = st.selectbox("Chord Progression", prog_names, index=prog_idx, key="w_progression")
        if progression != st.session_state.progression:
            st.session_state.progression = progression

    with harm_col2:
        hr_names = list(HARMONIC_RHYTHM.keys())
        hr_idx = hr_names.index(st.session_state.harmonic_rhythm) if st.session_state.harmonic_rhythm in hr_names else 0
        harmonic_rhythm = st.selectbox("Harmonic Rhythm", hr_names, index=hr_idx, key="w_harmonic_rhythm")
        if harmonic_rhythm != st.session_state.harmonic_rhythm:
            st.session_state.harmonic_rhythm = harmonic_rhythm

    with harm_col3:
        ext_names = list(CHORD_EXTENSIONS.keys())
        ext_idx = ext_names.index(st.session_state.extensions) if st.session_state.extensions in ext_names else 0
        extensions = st.selectbox("Chord Extensions", ext_names, index=ext_idx, key="w_extensions")
        if extensions != st.session_state.extensions:
            st.session_state.extensions = extensions


# =============================================================================
# SONG STRUCTURE
# =============================================================================

st.header("Song Structure")

# Add section button
add_col1, add_col2, add_col3 = st.columns([2, 2, 1])
with add_col1:
    new_section_type = st.selectbox("Add section", SECTION_TYPES, key="w_new_section_type")
with add_col2:
    new_section_instruments = st.text_input("Instruments (optional)", key="w_new_section_instruments")
with add_col3:
    st.write("")  # spacing
    if st.button("Add", use_container_width=True):
        st.session_state.sections.append({
            "id": str(uuid.uuid4()),
            "type": new_section_type,
            "instruments": new_section_instruments,
        })
        st.rerun()

# AI-suggest instruments button
suggest_col1, suggest_col2 = st.columns(2)
with suggest_col1:
    if st.button("AI Suggest Instruments", help="Fill empty instrument fields based on genre/mood"):
        st.session_state.sections = suggest_section_instruments(
            sections=st.session_state.sections,
            genre=st.session_state.genre,
            mood=st.session_state.mood,
            key=st.session_state.key,
            mode=st.session_state.mode,
            tempo=st.session_state.tempo,
            time_sig=st.session_state.time_sig,
            style_preset=st.session_state.style_preset,
            style_influence=st.session_state.style_influence,
            progression=st.session_state.progression,
            api_key=st.session_state.api_key if st.session_state.use_llm else None,
        )
        st.rerun()
with suggest_col2:
    if st.button("Clear All Instruments"):
        for s in st.session_state.sections:
            s["instruments"] = ""
        st.rerun()

# Conflict detection
if st.session_state.mood and st.session_state.mood != "None":
    conflicts = detect_section_conflicts(
        st.session_state.sections, st.session_state.genre, st.session_state.mood
    )
    if conflicts:
        for c in conflicts:
            st.warning(f"**{c['section']}**: {c['conflict']}. Try: {c['suggestion']}")

# Section editor
sections_to_remove = []
for i, section in enumerate(st.session_state.sections):
    sec_col1, sec_col2, sec_col3, sec_col4, sec_col5 = st.columns([1.5, 3, 0.5, 0.5, 0.5])

    with sec_col1:
        type_idx = SECTION_TYPES.index(section["type"]) if section["type"] in SECTION_TYPES else 0
        new_type = st.selectbox(
            "Type", SECTION_TYPES, index=type_idx,
            key=f"sec_type_{section['id']}",
            label_visibility="collapsed",
        )
        if new_type != section["type"]:
            st.session_state.sections[i]["type"] = new_type

    with sec_col2:
        new_instr = st.text_input(
            "Instruments", value=section["instruments"],
            key=f"sec_instr_{section['id']}",
            label_visibility="collapsed",
            placeholder="instruments, texture, energy...",
        )
        if new_instr != section["instruments"]:
            st.session_state.sections[i]["instruments"] = new_instr

    with sec_col3:
        if i > 0 and st.button("↑", key=f"up_{section['id']}"):
            st.session_state.sections[i], st.session_state.sections[i-1] = \
                st.session_state.sections[i-1], st.session_state.sections[i]
            st.rerun()

    with sec_col4:
        if i < len(st.session_state.sections) - 1 and st.button("↓", key=f"down_{section['id']}"):
            st.session_state.sections[i], st.session_state.sections[i+1] = \
                st.session_state.sections[i+1], st.session_state.sections[i]
            st.rerun()

    with sec_col5:
        if st.button("✕", key=f"rm_{section['id']}"):
            sections_to_remove.append(i)

# Remove sections marked for deletion
if sections_to_remove:
    for idx in sorted(sections_to_remove, reverse=True):
        st.session_state.sections.pop(idx)
    st.rerun()


# =============================================================================
# LYRICS
# =============================================================================

st.header("Lyrics")

lyrics_col1, lyrics_col2 = st.columns(2)

with lyrics_col1:
    suno_lyrics = st.text_area(
        "Paste Suno Lyrics (optional)",
        value=st.session_state.suno_lyrics,
        height=150,
        help="Paste existing lyrics with [Section] tags. They'll be merged with your structure.",
        key="w_suno_lyrics",
    )
    if suno_lyrics != st.session_state.suno_lyrics:
        st.session_state.suno_lyrics = suno_lyrics

    # Parse lyrics to sections
    if suno_lyrics.strip():
        if st.button("Import Sections from Lyrics"):
            parsed = parse_lyrics_to_sections(suno_lyrics)
            if parsed:
                st.session_state.sections = parsed
                st.success(f"Imported {len(parsed)} sections from lyrics")
                st.rerun()
            else:
                st.warning("No section tags found in lyrics")

with lyrics_col2:
    # Lyric template (Jazz-specific)
    if is_jazz:
        template_names = list(LYRIC_TEMPLATES.keys())
        template_idx = template_names.index(st.session_state.lyric_template) if st.session_state.lyric_template in template_names else 0
        lyric_template = st.selectbox(
            "Lyric Template",
            template_names,
            index=template_idx,
            help="Pre-built lyric structures for jazz compositions",
            key="w_lyric_template",
        )
        if lyric_template != st.session_state.lyric_template:
            st.session_state.lyric_template = lyric_template

        # Preview template
        if lyric_template != "None":
            template_content = LYRIC_TEMPLATES.get(lyric_template, "")
            if template_content:
                with st.expander("Template Preview"):
                    st.text(template_content[:500])


# =============================================================================
# GENERATE
# =============================================================================

st.divider()

gen_col1, gen_col2 = st.columns([3, 1])

with gen_col1:
    generate_clicked = st.button("Generate", type="primary", use_container_width=True)

with gen_col2:
    if st.button("Suggest Title"):
        title = suggest_song_title(
            genre=st.session_state.genre,
            mood=st.session_state.mood,
            key=st.session_state.key,
            mode=st.session_state.mode,
            use_llm=st.session_state.use_llm and bool(st.session_state.api_key),
            api_key=st.session_state.api_key,
            style_preset=st.session_state.style_preset,
            tempo=st.session_state.tempo,
            tech_context=st.session_state.tech_context,
            profile=st.session_state.profile,
            sections=st.session_state.sections,
        )
        st.session_state.suggested_title = title
        st.session_state.w_song_title = title
        st.rerun()

if generate_clicked:
    # Validate LLM mode
    if st.session_state.use_llm and not st.session_state.api_key:
        st.error("API key required for LLM generation. Add it in the sidebar.")
    else:
        with st.spinner("Generating..."):
            # Resolve harmony values
            prog_value = PROGRESSION_TYPES.get(st.session_state.progression, "")
            hr_value = HARMONIC_RHYTHM.get(st.session_state.harmonic_rhythm, "")
            ext_value = CHORD_EXTENSIONS.get(st.session_state.extensions, "")

            # Resolve key value
            key_value = resolve_key_value(st.session_state.key, st.session_state.key_quality)

            # Resolve mood value
            mood_value = MOOD_VARIATIONS.get(st.session_state.mood, "")

            # Resolve tempo value (for jazz)
            if is_jazz:
                tempo_value = TEMPO_VARIATIONS.get(st.session_state.tempo, "")
            else:
                tempo_value = st.session_state.tempo

            result = generate_outputs(
                genre=st.session_state.genre,
                key=key_value,
                mode=st.session_state.mode,
                tempo=tempo_value,
                time_sig=st.session_state.time_sig,
                mood=mood_value,
                sections=st.session_state.sections,
                suno_lyrics=st.session_state.suno_lyrics,
                lyric_template=st.session_state.lyric_template,
                style_preset=st.session_state.style_preset,
                style_influence=st.session_state.style_influence,
                progression=prog_value,
                harmonic_rhythm=hr_value,
                extensions=ext_value,
                replace_guitar=st.session_state.replace_guitar,
                use_llm=st.session_state.use_llm,
                api_key=st.session_state.api_key,
                profile=st.session_state.profile,
                tech_context=st.session_state.tech_context,
            )

            st.session_state.style_output = result["style"]
            st.session_state.lyrics_output = result["lyrics"]

            if result.get("cached"):
                st.info("Using cached LLM result")

        save_current_session()


# =============================================================================
# OUTPUT DISPLAY
# =============================================================================

if st.session_state.style_output or st.session_state.lyrics_output:
    st.header("Output")

    out_col1, out_col2 = st.columns(2)

    with out_col1:
        st.subheader("Style Field")
        st.text_area(
            "Style",
            value=st.session_state.style_output,
            height=200,
            key="w_style_display",
            label_visibility="collapsed",
        )
        char_count = len(st.session_state.style_output)
        color = "red" if char_count > 1000 else "orange" if char_count > 800 else "green"
        st.markdown(f":{color}[{char_count}/1000 characters]")

    with out_col2:
        st.subheader("Lyrics Field")
        st.text_area(
            "Lyrics",
            value=st.session_state.lyrics_output,
            height=200,
            key="w_lyrics_display",
            label_visibility="collapsed",
        )

    # Lyrics validation
    if st.session_state.lyrics_output:
        validation = validate_lyrics_format(st.session_state.lyrics_output)
        if validation.get("warnings"):
            for w in validation["warnings"]:
                st.warning(w)
        if validation.get("suggestions"):
            with st.expander("Suggestions"):
                for s in validation["suggestions"]:
                    st.caption(f"- {s}")

    # ==========================================================================
    # AI REFINEMENT
    # ==========================================================================

    st.subheader("AI Refinement")

    refine_col1, refine_col2 = st.columns(2)

    # ── Quick Refine (existing one-shot) ──────────────────────────────────
    with refine_col1:
        if st.button("Quick Refine", help="One-shot analysis and improvement"):
            if not st.session_state.api_key:
                st.error("API key required for AI refinement.")
            else:
                with st.spinner("Refining..."):
                    try:
                        refine_result = run_refinement_agent(
                            style_text=st.session_state.style_output,
                            lyrics_text=st.session_state.lyrics_output,
                            api_key=st.session_state.api_key,
                            is_jazz=is_jazz,
                            genre=st.session_state.genre,
                            mood=st.session_state.mood,
                            profile=st.session_state.profile,
                        )

                        score_col1, score_col2, score_col3 = st.columns(3)
                        score_col1.metric("Style Score", f"{refine_result['style_score']}/10")
                        score_col2.metric("Lyrics Score", f"{refine_result['lyrics_score']}/10")
                        overall = round((refine_result['style_score'] + refine_result['lyrics_score']) / 2)
                        score_col3.metric("Overall", f"{overall}/10")

                        with st.expander("Reasoning Steps"):
                            for step in refine_result.get("reasoning", []):
                                if "action" in step:
                                    st.caption(f"Called: {step['action']}")
                                if "observation" in step:
                                    st.caption(f"Result: {step['observation']}")

                        ref_col1, ref_col2 = st.columns(2)
                        with ref_col1:
                            st.text_area("Refined Style", value=refine_result["refined_style"],
                                         height=200, key="w_refined_style")
                        with ref_col2:
                            st.text_area("Refined Lyrics", value=refine_result["refined_lyrics"],
                                         height=200, key="w_refined_lyrics")

                        if st.button("Accept Refinement"):
                            st.session_state.style_output = refine_result["refined_style"]
                            st.session_state.lyrics_output = refine_result["refined_lyrics"]
                            save_current_session()
                            st.rerun()

                    except Exception as e:
                        st.error(f"Refinement failed: {e}")

    # ── Iterative Refinement ──────────────────────────────────────────────
    with refine_col2:
        if not st.session_state.iter_active:
            if st.button("Refine with Suggestions",
                         help="Get AI suggestions and refine iteratively"):
                if not st.session_state.api_key:
                    st.error("API key required.")
                elif not st.session_state.style_output:
                    st.error("Generate a prompt first.")
                else:
                    # Save original as version 0
                    st.session_state.iter_versions = [{
                        "version": 0,
                        "style": st.session_state.style_output,
                        "lyrics": st.session_state.lyrics_output,
                        "suggestions_shown": [],
                        "suggestions_applied": [],
                        "user_feedback": "",
                    }]
                    with st.spinner("Analyzing..."):
                        try:
                            suggestions = generate_suggestions(
                                style_text=st.session_state.style_output,
                                lyrics_text=st.session_state.lyrics_output,
                                api_key=st.session_state.api_key,
                                is_jazz=is_jazz,
                                genre=st.session_state.genre,
                                mood=st.session_state.mood,
                                profile=st.session_state.profile,
                            )
                            st.session_state.iter_suggestions = suggestions
                            st.session_state.iter_active = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
        else:
            if st.button("Close Suggestions"):
                st.session_state.iter_active = False
                st.session_state.iter_suggestions = []
                st.session_state.iter_versions = []
                st.rerun()

    # ── Suggestions Panel (when active) ───────────────────────────────────
    if st.session_state.iter_active and st.session_state.iter_suggestions:
        current_version = len(st.session_state.iter_versions) - 1
        current = st.session_state.iter_versions[-1]

        st.divider()
        st.caption(f"Version {current_version} — select suggestions to apply")

        # Display current outputs
        iter_out_col1, iter_out_col2 = st.columns(2)
        with iter_out_col1:
            st.text_area("Current Style", value=current["style"],
                         height=150, key="w_iter_style_display", disabled=True)
        with iter_out_col2:
            st.text_area("Current Lyrics", value=current["lyrics"],
                         height=150, key="w_iter_lyrics_display", disabled=True)

        # Suggestion checkboxes
        category_icons = {
            "instrumentation": "Instruments",
            "harmony": "Harmony",
            "mood": "Mood",
            "structure": "Structure",
            "technical": "Technical",
        }

        for sugg in st.session_state.iter_suggestions:
            cat_label = category_icons.get(sugg["category"], sugg["category"])
            checked = st.checkbox(
                f"**[{cat_label}]** {sugg['title']}",
                key=f"iter_check_{sugg['id']}",
                help=sugg["description"],
            )
            st.caption(f"  {sugg['description']}")
            has_preview = (
                sugg.get("preview_style", "no change") != "no change"
                or sugg.get("preview_lyrics", "no change") != "no change"
            )
            if has_preview:
                with st.expander(f"Preview: {sugg['title']}", expanded=False):
                    if sugg.get("preview_style", "no change") != "no change":
                        st.text(f"Style: {sugg['preview_style']}")
                    if sugg.get("preview_lyrics", "no change") != "no change":
                        st.text(f"Lyrics: {sugg['preview_lyrics']}")

        # Custom feedback
        user_feedback = st.text_input(
            "Additional direction (optional)",
            placeholder="e.g., make it warmer, add more space...",
            key="w_iter_feedback",
        )

        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            apply_clicked = st.button("Apply Selected", type="primary")

        with btn_col2:
            analyze_again = st.button("Re-analyze")

        with btn_col3:
            accept_close = st.button("Accept & Close")

        # Handle Apply
        if apply_clicked:
            selected = [
                s for s in st.session_state.iter_suggestions
                if st.session_state.get(f"iter_check_{s['id']}", False)
            ]
            if not selected and not user_feedback.strip():
                st.warning("Select at least one suggestion or provide feedback.")
            else:
                with st.spinner("Applying refinements..."):
                    try:
                        result = apply_suggestions(
                            style_text=current["style"],
                            lyrics_text=current["lyrics"],
                            selected_suggestions=selected,
                            user_feedback=user_feedback,
                            api_key=st.session_state.api_key,
                            is_jazz=is_jazz,
                            genre=st.session_state.genre,
                            mood=st.session_state.mood,
                            profile=st.session_state.profile,
                        )

                        # Save new version
                        new_version = {
                            "version": current_version + 1,
                            "style": result["refined_style"],
                            "lyrics": result["refined_lyrics"],
                            "suggestions_shown": list(st.session_state.iter_suggestions),
                            "suggestions_applied": [s["id"] for s in selected],
                            "user_feedback": user_feedback,
                        }
                        st.session_state.iter_versions.append(new_version)

                        # Auto-analyze new version
                        new_suggestions = generate_suggestions(
                            style_text=result["refined_style"],
                            lyrics_text=result["refined_lyrics"],
                            api_key=st.session_state.api_key,
                            is_jazz=is_jazz,
                            genre=st.session_state.genre,
                            mood=st.session_state.mood,
                            profile=st.session_state.profile,
                            iteration_history=st.session_state.iter_versions,
                        )
                        st.session_state.iter_suggestions = new_suggestions
                        st.rerun()
                    except Exception as e:
                        st.error(f"Apply failed: {e}")

        # Handle Re-analyze (same version, fresh suggestions)
        if analyze_again:
            with st.spinner("Re-analyzing..."):
                try:
                    suggestions = generate_suggestions(
                        style_text=current["style"],
                        lyrics_text=current["lyrics"],
                        api_key=st.session_state.api_key,
                        is_jazz=is_jazz,
                        genre=st.session_state.genre,
                        mood=st.session_state.mood,
                        profile=st.session_state.profile,
                        iteration_history=st.session_state.iter_versions,
                    )
                    st.session_state.iter_suggestions = suggestions
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        # Handle Accept & Close
        if accept_close:
            final = st.session_state.iter_versions[-1]
            st.session_state.style_output = final["style"]
            st.session_state.lyrics_output = final["lyrics"]
            st.session_state.iter_active = False
            st.session_state.iter_suggestions = []
            st.session_state.iter_versions = []
            save_current_session()
            st.rerun()

        # Version History
        if len(st.session_state.iter_versions) > 1:
            with st.expander("Version History"):
                for v in st.session_state.iter_versions:
                    ver_num = v["version"]
                    label = "Original" if ver_num == 0 else f"Version {ver_num}"

                    # Show applied suggestions in label
                    if v.get("suggestions_applied"):
                        applied_titles = []
                        for s in v.get("suggestions_shown", []):
                            if s.get("id") in v["suggestions_applied"]:
                                applied_titles.append(s.get("title", ""))
                        if applied_titles:
                            short = ", ".join(applied_titles[:2])
                            if len(applied_titles) > 2:
                                short += "..."
                            label += f" ({short})"

                    if v.get("user_feedback"):
                        label += f' + "{v["user_feedback"][:30]}..."'

                    if st.button(label, key=f"iter_ver_{ver_num}"):
                        # Revert to this version
                        st.session_state.iter_versions = st.session_state.iter_versions[:ver_num + 1]
                        with st.spinner("Re-analyzing..."):
                            try:
                                suggestions = generate_suggestions(
                                    style_text=v["style"],
                                    lyrics_text=v["lyrics"],
                                    api_key=st.session_state.api_key,
                                    is_jazz=is_jazz,
                                    genre=st.session_state.genre,
                                    mood=st.session_state.mood,
                                    profile=st.session_state.profile,
                                    iteration_history=st.session_state.iter_versions,
                                )
                                st.session_state.iter_suggestions = suggestions
                            except Exception as e:
                                st.error(f"Analysis failed: {e}")
                        st.rerun()

    # ==========================================================================
    # SAVE SONG
    # ==========================================================================

    st.divider()
    st.subheader("Save Song")

    save_col1, save_col2 = st.columns([3, 1])
    with save_col1:
        default_title = st.session_state.get("suggested_title", "")
        song_title = st.text_input("Song Title", value=default_title, key="w_song_title")
    with save_col2:
        st.write("")  # spacing
        if st.button("Save to History", use_container_width=True):
            if not song_title:
                st.warning("Enter a title first.")
            else:
                settings = {
                    "genre": st.session_state.genre,
                    "key": st.session_state.key,
                    "mode": st.session_state.mode,
                    "tempo": st.session_state.tempo,
                    "time_sig": st.session_state.time_sig,
                    "mood": st.session_state.mood,
                    "style_preset": st.session_state.style_preset,
                    "style_influence": st.session_state.style_influence,
                    "progression": st.session_state.progression,
                    "harmonic_rhythm": st.session_state.harmonic_rhythm,
                    "extensions": st.session_state.extensions,
                    "profile": st.session_state.profile,
                    "sections": st.session_state.sections,
                }
                save_song(
                    title=song_title,
                    settings=settings,
                    style_output=st.session_state.style_output,
                    lyrics_output=st.session_state.lyrics_output,
                )
                st.success(f"Saved: {song_title}")
                save_current_session()


# =============================================================================
# AUTO-SAVE WORKING SESSION
# =============================================================================

save_current_session()
