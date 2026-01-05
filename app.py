import os
import streamlit as st
import random
import csv
import io
from prompt_engine import build_prompt
from data import (
    TONALITY_MODES, MODE_FAMILIES, GUITAR_VARIATIONS, GROOVE_VARIATIONS,
    TEMPO_VARIATIONS, MOOD_VARIATIONS, ERA_VARIATIONS, INTRO_VARIATIONS
)
from storage import load_history, save_song, delete_song
from refiner import run_refinement_agent

st.set_page_config(page_title="Suno Prompt Generator", layout="wide")

# Parameter groups for lock mode
PARAM_GROUPS = {
    "Sound": ["tonality", "mood"],
    "Style": ["mode_family", "era"],
    "Rhythm": ["groove", "tempo"],
    "Instrument": ["guitar"],
    "Arrangement": ["intro"]
}

ALL_PARAMS = {
    "tonality": TONALITY_MODES,
    "mode_family": MODE_FAMILIES,
    "guitar": GUITAR_VARIATIONS,
    "groove": GROOVE_VARIATIONS,
    "tempo": TEMPO_VARIATIONS,
    "mood": MOOD_VARIATIONS,
    "era": ERA_VARIATIONS,
    "intro": INTRO_VARIATIONS
}

# Sidebar - Song History & Tools
with st.sidebar:
    st.header("Saved Songs")
    history = load_history()

    if history:
        # CSV Export
        if st.button("Export to CSV"):
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Title", "Timestamp", "Tonality", "Mode Family", "Guitar",
                           "Groove", "Tempo", "Mood", "Era", "Intro", "Prompt"])
            for song in history:
                s = song["settings"]
                writer.writerow([
                    song["title"], song["timestamp"],
                    s.get("tonality", ""), s.get("mode_family", ""), s.get("guitar", ""),
                    s.get("groove", ""), s.get("tempo", ""), s.get("mood", ""), s.get("era", ""),
                    s.get("intro", ""), song["prompt"]
                ])
            st.download_button(
                "Download CSV",
                output.getvalue(),
                file_name="suno_songs.csv",
                mime="text/csv"
            )

        st.divider()

        for i, song in enumerate(reversed(history)):
            idx = len(history) - 1 - i
            with st.expander(song["title"] or f"Untitled ({song['timestamp'][:10]})"):
                st.caption(song["timestamp"][:16].replace("T", " "))
                st.text(song["prompt"][:100] + "..." if len(song["prompt"]) > 100 else song["prompt"])
                col1, col2 = st.columns(2)
                if col1.button("Load", key=f"load_{idx}"):
                    st.session_state["loaded_settings"] = song["settings"]
                    st.session_state["loaded_title"] = song["title"]
                    st.rerun()
                if col2.button("Delete", key=f"del_{idx}"):
                    delete_song(idx)
                    st.rerun()
    else:
        st.caption("No saved songs yet")

# Main content
st.title("Suno Prompt Generator")

# Get loaded settings if any
loaded = st.session_state.get("loaded_settings", {})

# Parameter selection
col1, col2 = st.columns(2)

with col1:
    tonality_keys = list(TONALITY_MODES.keys())
    tonality_idx = tonality_keys.index(loaded.get("tonality", "None")) if loaded.get("tonality") in tonality_keys else 0
    tonality = st.selectbox("Tonality", tonality_keys, index=tonality_idx)

    mode_keys = list(MODE_FAMILIES.keys())
    mode_idx = mode_keys.index(loaded.get("mode_family", "None")) if loaded.get("mode_family") in mode_keys else 0
    mode_family = st.selectbox("Mode Family", mode_keys, index=mode_idx)

    guitar_keys = list(GUITAR_VARIATIONS.keys())
    guitar_idx = guitar_keys.index(loaded.get("guitar", "None")) if loaded.get("guitar") in guitar_keys else 0
    guitar = st.selectbox("Guitar Style", guitar_keys, index=guitar_idx)

    groove_keys = list(GROOVE_VARIATIONS.keys())
    groove_idx = groove_keys.index(loaded.get("groove", "None")) if loaded.get("groove") in groove_keys else 0
    groove = st.selectbox("Groove", groove_keys, index=groove_idx)

with col2:
    tempo_keys = list(TEMPO_VARIATIONS.keys())
    tempo_idx = tempo_keys.index(loaded.get("tempo", "None")) if loaded.get("tempo") in tempo_keys else 0
    tempo = st.selectbox("Tempo", tempo_keys, index=tempo_idx)

    mood_keys = list(MOOD_VARIATIONS.keys())
    mood_idx = mood_keys.index(loaded.get("mood", "None")) if loaded.get("mood") in mood_keys else 0
    mood = st.selectbox("Mood", mood_keys, index=mood_idx)

    era_keys = list(ERA_VARIATIONS.keys())
    era_idx = era_keys.index(loaded.get("era", "None")) if loaded.get("era") in era_keys else 0
    era = st.selectbox("Era/Style", era_keys, index=era_idx)

    intro_keys = list(INTRO_VARIATIONS.keys())
    intro_idx = intro_keys.index(loaded.get("intro", "None")) if loaded.get("intro") in intro_keys else 0
    intro = st.selectbox("Intro Style", intro_keys, index=intro_idx)

# Current selections dict
current_selections = {
    "tonality": tonality,
    "mode_family": mode_family,
    "guitar": guitar,
    "groove": groove,
    "tempo": tempo,
    "mood": mood,
    "era": era,
    "intro": intro
}

# Auto-generate song title from selections (max 80 chars)
def build_auto_title(selections, max_len=80):
    parts = [v for k, v in selections.items() if v != "None"]
    if not parts:
        return "Default Jazz"
    title = " | ".join(parts)
    if len(title) <= max_len:
        return title
    # Truncate and add ellipsis
    return title[:max_len - 3] + "..."

auto_title = build_auto_title(current_selections)
loaded_title = st.session_state.get("loaded_title", "")

st.divider()
song_title = st.text_input(
    "Song Title",
    value=loaded_title if loaded_title else auto_title,
    max_chars=80,
    help="Auto-generated from your selections. Max 80 characters."
)

# Clear loaded settings after use
if "loaded_settings" in st.session_state:
    del st.session_state["loaded_settings"]
if "loaded_title" in st.session_state:
    del st.session_state["loaded_title"]

# Generate prompt
st.divider()
prompt = build_prompt(
    TONALITY_MODES[tonality],
    MODE_FAMILIES[mode_family],
    GUITAR_VARIATIONS[guitar],
    GROOVE_VARIATIONS[groove],
    TEMPO_VARIATIONS[tempo],
    MOOD_VARIATIONS[mood],
    ERA_VARIATIONS[era],
    INTRO_VARIATIONS[intro]
)

st.subheader("Generated Prompt")
st.text_area("", prompt, height=150, label_visibility="collapsed")

# Save button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("Save Song", type="primary"):
        save_song(song_title or "Untitled", current_selections, prompt)
        st.success("Song saved!")
        st.rerun()

# AI Prompt Refiner Agent Section
st.divider()
st.subheader("AI Prompt Refiner Agent")

# API Key handling - check env var first, then session state
env_api_key = os.environ.get("OPENAI_API_KEY", "")
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = env_api_key

api_key_input = st.text_input(
    "OpenAI API Key",
    value=st.session_state["openai_api_key"],
    type="password",
    help="Your API key is stored in session only (not saved to disk). You can also set OPENAI_API_KEY environment variable."
)
st.session_state["openai_api_key"] = api_key_input

refine_col1, refine_col2 = st.columns([1, 4])
with refine_col1:
    refine_button = st.button("Refine with Agent")

if refine_button:
    if not st.session_state["openai_api_key"]:
        st.error("Please enter your OpenAI API key")
    else:
        with st.spinner("Agent is analyzing and refining your prompt..."):
            try:
                result = run_refinement_agent(prompt, st.session_state["openai_api_key"])
                st.session_state["refined_prompt"] = result["refined_prompt"]
                st.session_state["refine_score"] = result["score"]
                st.session_state["refine_reasoning"] = result["reasoning"]
            except Exception as e:
                st.error(f"Error refining prompt: {str(e)}")

# Display refined prompt if available
if "refined_prompt" in st.session_state and st.session_state["refined_prompt"]:
    # Show agent reasoning in expander
    if "refine_reasoning" in st.session_state and st.session_state["refine_reasoning"]:
        with st.expander("Agent Reasoning Steps", expanded=False):
            for step in st.session_state["refine_reasoning"]:
                if "action" in step:
                    st.markdown(f"**Action:** `{step['action']}`")
                    if "input" in step:
                        st.caption(f"Input: {step['input']}")
                elif "observation" in step:
                    st.markdown(f"**Observation:** {step['observation']}")
                    if "details" in step:
                        st.caption(step["details"])
                st.divider()

    # Show score
    score = st.session_state.get("refine_score", 7)
    score_color = "green" if score >= 8 else "orange" if score >= 6 else "red"
    st.subheader(f"Refined Prompt (Score: :{score_color}[{score}/10])")

    st.text_area("", st.session_state["refined_prompt"], height=150, key="refined_display", label_visibility="collapsed")

    ref_col1, ref_col2, ref_col3 = st.columns([1, 1, 3])
    with ref_col1:
        if st.button("Save Refined", type="primary"):
            save_song(
                (song_title or "Untitled") + " (Refined)",
                current_selections,
                st.session_state["refined_prompt"]
            )
            st.success("Refined prompt saved!")
            st.rerun()
    with ref_col2:
        if st.button("Clear Refined"):
            if "refined_prompt" in st.session_state:
                del st.session_state["refined_prompt"]
            if "refine_score" in st.session_state:
                del st.session_state["refine_score"]
            if "refine_reasoning" in st.session_state:
                del st.session_state["refine_reasoning"]
            st.rerun()

# Batch Generation Section
st.divider()
st.subheader("Batch Generation")

# Lock groups
st.write("**Lock parameter groups** (locked groups keep current values)")
lock_cols = st.columns(len(PARAM_GROUPS))
locked_groups = []
for i, (group_name, _) in enumerate(PARAM_GROUPS.items()):
    with lock_cols[i]:
        if st.checkbox(group_name, key=f"lock_{group_name}"):
            locked_groups.append(group_name)

# Get locked parameters
locked_params = set()
for group in locked_groups:
    locked_params.update(PARAM_GROUPS[group])

batch_col1, batch_col2 = st.columns([1, 3])
with batch_col1:
    batch_count = st.number_input("Variations", min_value=1, max_value=20, value=5)

if st.button("Generate Batch"):
    batch_results = []

    for i in range(batch_count):
        # Generate random selections, respecting locks
        batch_selections = {}
        for param, options in ALL_PARAMS.items():
            if param in locked_params:
                batch_selections[param] = current_selections[param]
            else:
                # Random selection (skip "None" for variety, 20% chance of None)
                keys = list(options.keys())
                if random.random() < 0.2:
                    batch_selections[param] = "None"
                else:
                    non_none = [k for k in keys if k != "None"]
                    batch_selections[param] = random.choice(non_none) if non_none else "None"

        # Build prompt for this variation
        batch_prompt = build_prompt(
            TONALITY_MODES[batch_selections["tonality"]],
            MODE_FAMILIES[batch_selections["mode_family"]],
            GUITAR_VARIATIONS[batch_selections["guitar"]],
            GROOVE_VARIATIONS[batch_selections["groove"]],
            TEMPO_VARIATIONS[batch_selections["tempo"]],
            MOOD_VARIATIONS[batch_selections["mood"]],
            ERA_VARIATIONS[batch_selections["era"]],
            INTRO_VARIATIONS[batch_selections["intro"]]
        )

        batch_title = build_auto_title(batch_selections)
        batch_results.append({
            "title": batch_title,
            "selections": batch_selections,
            "prompt": batch_prompt
        })

    st.session_state["batch_results"] = batch_results

# Display batch results
if "batch_results" in st.session_state and st.session_state["batch_results"]:
    st.write("**Generated Variations:**")

    for i, result in enumerate(st.session_state["batch_results"]):
        with st.expander(f"{i+1}. {result['title'][:60]}..."):
            st.text_area("Prompt", result["prompt"], height=100, key=f"batch_prompt_{i}")
            if st.button("Save This Variation", key=f"save_batch_{i}"):
                save_song(result["title"], result["selections"], result["prompt"])
                st.success("Saved!")
                st.rerun()

    # Export batch to CSV
    if st.button("Export Batch to CSV"):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Title", "Tonality", "Mode Family", "Guitar",
                       "Groove", "Tempo", "Mood", "Era", "Intro", "Prompt"])
        for result in st.session_state["batch_results"]:
            s = result["selections"]
            writer.writerow([
                result["title"],
                s["tonality"], s["mode_family"], s["guitar"],
                s["groove"], s["tempo"], s["mood"], s["era"],
                s["intro"], result["prompt"]
            ])
        st.download_button(
            "Download Batch CSV",
            output.getvalue(),
            file_name="suno_batch.csv",
            mime="text/csv"
        )
