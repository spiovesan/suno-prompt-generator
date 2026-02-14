"""
Suno Workflow Builder - Generate Style and Lyrics fields for Suno AI.

Run with: streamlit run workflow_builder/app.py
"""

import os
import streamlit as st
from data import (
    MAJOR_KEYS, MINOR_KEYS, MODES, TIME_SIGNATURES,
    TEMPO_RANGES, GENRES, SECTION_TYPES, POETIC_METERS,
    DEFAULT_SECTIONS
)
from generator import build_style_output, build_lyrics_output
from refiner import run_refinement_agent

st.set_page_config(
    page_title="Suno Workflow Builder",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 Suno Workflow Builder")
st.caption("Generate Style and Lyrics fields for Suno AI music generation")

# Initialize session state for sections
if "sections" not in st.session_state:
    st.session_state.sections = [
        {"type": "Intro", "instruments": "ambient pads, soft piano"},
        {"type": "Verse", "instruments": "acoustic guitar, mellow tone"},
        {"type": "Chorus", "instruments": "full band, high energy"},
        {"type": "Bridge", "instruments": "synth arpeggios, rising tension"},
        {"type": "Outro", "instruments": "fade out, ambient"},
    ]

# --- MUSIC FOUNDATION ---
st.header("🎹 Music Foundation")

col1, col2, col3 = st.columns(3)

with col1:
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

with col2:
    selected_mode = st.selectbox(
        "Mode",
        options=list(MODES.keys()),
        index=0,
        help="Modal flavor that affects emotional color"
    )
    mode_info = MODES[selected_mode]
    st.caption(f"_{mode_info['mood']}_")

with col3:
    selected_time_sig = st.selectbox(
        "Time Signature",
        options=list(TIME_SIGNATURES.keys()),
        index=0,
        help="Beat grouping that defines the groove"
    )
    st.caption(f"_{TIME_SIGNATURES[selected_time_sig]}_")

col4, col5 = st.columns(2)

with col4:
    selected_tempo = st.selectbox(
        "Tempo",
        options=list(TEMPO_RANGES.keys()),
        index=1,  # Default to mid-tempo
        help="Speed and energy of the song"
    )
    st.caption(f"_{TEMPO_RANGES[selected_tempo]}_")

with col5:
    selected_genre = st.selectbox(
        "Genre",
        options=GENRES,
        index=0,
        help="Primary genre for audio quality template"
    )

# --- SONG STRUCTURE ---
st.divider()
st.header("📝 Song Structure (Meta Tags)")
st.caption("Define your song sections with instrument/mood descriptors")

# Add section button
col_add, col_preset = st.columns([1, 2])
with col_add:
    if st.button("+ Add Section"):
        st.session_state.sections.append({"type": "Verse", "instruments": ""})
        st.rerun()

with col_preset:
    preset_genre = st.selectbox(
        "Load preset structure",
        options=["-- Select --"] + list(DEFAULT_SECTIONS.keys()),
        key="preset_select"
    )
    if preset_genre != "-- Select --":
        preset_sections = DEFAULT_SECTIONS.get(preset_genre, DEFAULT_SECTIONS["default"])
        st.session_state.sections = [
            {"type": s, "instruments": ""} for s in preset_sections
        ]
        st.rerun()

# Display sections
sections_to_remove = []
for i, section in enumerate(st.session_state.sections):
    col_type, col_instr, col_del = st.columns([1, 3, 0.3])

    with col_type:
        new_type = st.selectbox(
            f"Section {i+1}",
            options=SECTION_TYPES,
            index=SECTION_TYPES.index(section["type"]) if section["type"] in SECTION_TYPES else 0,
            key=f"section_type_{i}",
            label_visibility="collapsed"
        )
        st.session_state.sections[i]["type"] = new_type

    with col_instr:
        new_instr = st.text_input(
            f"Instruments {i+1}",
            value=section.get("instruments", ""),
            key=f"section_instr_{i}",
            placeholder="e.g., acoustic guitar, mellow tone",
            label_visibility="collapsed"
        )
        st.session_state.sections[i]["instruments"] = new_instr

    with col_del:
        if st.button("✕", key=f"del_{i}", help="Remove section"):
            sections_to_remove.append(i)

# Remove marked sections
if sections_to_remove:
    for i in sorted(sections_to_remove, reverse=True):
        st.session_state.sections.pop(i)
    st.rerun()

# --- OPTIONAL LYRICS ---
st.divider()
st.header("🎤 Lyrics (Optional)")
st.caption("Paste or write your lyrics here — they'll appear after the meta tags")

lyrics_text = st.text_area(
    "Lyrics",
    height=150,
    placeholder="Enter your lyrics here...\nThey will be included after the structure tags.",
    label_visibility="collapsed"
)

# --- POETIC METER REFERENCE (Collapsed) ---
with st.expander("📚 Poetic Meter Reference"):
    for meter_name, meter_info in POETIC_METERS.items():
        st.markdown(f"**{meter_name}**")
        st.caption(f"Pattern: {meter_info['pattern']} | Feel: {meter_info['feel']}")
        st.caption(f"Example: _{meter_info['example']}_")
        st.caption(f"Best for: {meter_info['genres']}")
        st.markdown("---")

# --- GENERATE OUTPUTS ---
st.divider()

if st.button("🎵 Generate Outputs", type="primary", use_container_width=True):
    # Build outputs
    style_output = build_style_output(selected_genre)
    lyrics_output = build_lyrics_output(
        key=selected_key if selected_key != "None" else "",
        mode=selected_mode,
        tempo=selected_tempo,
        time_sig=selected_time_sig,
        genre=selected_genre,
        sections=st.session_state.sections,
        lyrics_text=lyrics_text
    )

    st.session_state.generated_style = style_output
    st.session_state.generated_lyrics = lyrics_output

# Display outputs if generated
if "generated_style" in st.session_state:
    st.header("📋 Generated Outputs")

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

    # --- REFINER SECTION ---
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
                        api_key
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

    # Display refined outputs if available
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

        # Show reasoning in expander
        with st.expander("🔍 Refinement Reasoning"):
            for step in st.session_state.refiner_reasoning:
                if "action" in step:
                    st.markdown(f"**Action:** `{step['action']}`")
                if "observation" in step:
                    st.markdown(f"→ {step['observation']}")
                if "details" in step:
                    st.caption(step["details"])

# --- SIDEBAR INFO ---
with st.sidebar:
    st.header("Settings")

    # API Key input
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=os.environ.get("OPENAI_API_KEY", ""),
        type="password",
        help="Required for AI refinement. Set OPENAI_API_KEY env var to pre-fill."
    )
    st.session_state["openai_api_key"] = api_key_input

    st.divider()

    st.header("About")
    st.markdown("""
    This tool generates **two outputs** for Suno:

    1. **Style Field**: Pro audio quality prompt
    2. **Lyrics Field**: Meta tags + structure

    ### How to use:
    1. Select your music foundation (key, mode, tempo, etc.)
    2. Build your song structure with sections
    3. Optionally add lyrics
    4. Click Generate
    5. (Optional) Click Refine to improve with AI
    6. Copy each output to the corresponding Suno field
    """)

    st.divider()
    st.caption("Based on [suno_workflow.md](../docs/suno_workflow.md)")
