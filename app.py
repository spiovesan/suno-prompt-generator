import os
import streamlit as st
import random
import csv
import io
from prompt_engine import build_prompt
from data import (
    STYLE_PRESETS, KEY_SIGNATURES, STYLE_INFLUENCES,
    TEMPO_VARIATIONS, MOOD_VARIATIONS, INTRO_VARIATIONS,
    PROGRESSION_TYPES, HARMONIC_RHYTHM, CHORD_EXTENSIONS,
    LYRIC_TEMPLATES
)
from storage import load_history, save_song, delete_song
from refiner import run_refinement_agent
from llm_generator import generate_prompt

st.set_page_config(page_title="Suno Prompt Generator", layout="wide")

# Parameter groups for lock mode (simplified)
PARAM_GROUPS = {
    "Core": ["style_preset", "key_signature", "style_influence"],
    "Feel": ["tempo", "mood"],
    "Arrangement": ["intro"],
    "Harmony": ["progression", "harmonic_rhythm", "extensions"],
    "Lyrics": ["lyric_template"]
}

ALL_PARAMS = {
    "style_preset": {k: k for k in STYLE_PRESETS.keys()},
    "key_signature": KEY_SIGNATURES,
    "style_influence": STYLE_INFLUENCES,
    "tempo": TEMPO_VARIATIONS,
    "mood": MOOD_VARIATIONS,
    "intro": INTRO_VARIATIONS,
    "progression": PROGRESSION_TYPES,
    "harmonic_rhythm": HARMONIC_RHYTHM,
    "extensions": CHORD_EXTENSIONS,
    "lyric_template": LYRIC_TEMPLATES
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
            writer.writerow(["Title", "Timestamp", "Style Preset", "Key", "Style Influence",
                           "Tempo", "Mood", "Intro", "Progression", "Harmonic Rhythm", "Extensions",
                           "Lyric Template", "Prompt", "Lyrics"])
            for song in history:
                s = song["settings"]
                writer.writerow([
                    song["title"], song["timestamp"],
                    s.get("style_preset", ""), s.get("key_signature", ""), s.get("style_influence", ""),
                    s.get("tempo", ""), s.get("mood", ""), s.get("intro", ""),
                    s.get("progression", ""), s.get("harmonic_rhythm", ""), s.get("extensions", ""),
                    s.get("lyric_template", ""),
                    song["prompt"],
                    song.get("lyrics", "")
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
                if song.get("lyrics"):
                    st.caption("Has lyrics template")
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

# Core Style Selection
st.subheader("Core Style")
core_col1, core_col2, core_col3 = st.columns(3)

with core_col1:
    style_preset_keys = list(STYLE_PRESETS.keys())
    style_preset_idx = style_preset_keys.index(loaded.get("style_preset", "Smooth Jazz")) if loaded.get("style_preset") in style_preset_keys else 0
    style_preset = st.selectbox("Style Preset", style_preset_keys, index=style_preset_idx,
                                help="Foundation style - dramatically changes the entire sound")

with core_col2:
    key_keys = list(KEY_SIGNATURES.keys())
    key_idx = key_keys.index(loaded.get("key_signature", "None")) if loaded.get("key_signature") in key_keys else 0
    key_signature = st.selectbox("Key Signature", key_keys, index=key_idx,
                                 help="Explicit key for harmonic direction")

with core_col3:
    influence_keys = list(STYLE_INFLUENCES.keys())
    influence_idx = influence_keys.index(loaded.get("style_influence", "None")) if loaded.get("style_influence") in influence_keys else 0
    style_influence = st.selectbox("Style Influence", influence_keys, index=influence_idx,
                                   help="Era and style-inspired sound characteristics")

st.divider()

# Feel parameters
st.subheader("Feel")
feel_col1, feel_col2, feel_col3 = st.columns(3)

with feel_col1:
    tempo_keys = list(TEMPO_VARIATIONS.keys())
    tempo_idx = tempo_keys.index(loaded.get("tempo", "None")) if loaded.get("tempo") in tempo_keys else 0
    tempo = st.selectbox("Tempo", tempo_keys, index=tempo_idx)

with feel_col2:
    mood_keys = list(MOOD_VARIATIONS.keys())
    mood_idx = mood_keys.index(loaded.get("mood", "None")) if loaded.get("mood") in mood_keys else 0
    mood = st.selectbox("Mood", mood_keys, index=mood_idx)

with feel_col3:
    intro_keys = list(INTRO_VARIATIONS.keys())
    intro_idx = intro_keys.index(loaded.get("intro", "None")) if loaded.get("intro") in intro_keys else 0
    intro = st.selectbox("Intro Style", intro_keys, index=intro_idx)

# Harmony parameters - avoid boring IVm7-Im7 progressions
st.divider()
st.subheader("Harmony")
harm_col1, harm_col2, harm_col3 = st.columns(3)

with harm_col1:
    prog_keys = list(PROGRESSION_TYPES.keys())
    prog_idx = prog_keys.index(loaded.get("progression", "None")) if loaded.get("progression") in prog_keys else 0
    progression = st.selectbox("Chord Progression", prog_keys, index=prog_idx,
                               help="Specific progression type - avoids boring IVm7-Im7")

with harm_col2:
    rhythm_keys = list(HARMONIC_RHYTHM.keys())
    rhythm_idx = rhythm_keys.index(loaded.get("harmonic_rhythm", "None")) if loaded.get("harmonic_rhythm") in rhythm_keys else 0
    harmonic_rhythm = st.selectbox("Harmonic Rhythm", rhythm_keys, index=rhythm_idx,
                                   help="How often chords change")

with harm_col3:
    ext_keys = list(CHORD_EXTENSIONS.keys())
    ext_idx = ext_keys.index(loaded.get("extensions", "None")) if loaded.get("extensions") in ext_keys else 0
    extensions = st.selectbox("Chord Extensions", ext_keys, index=ext_idx,
                              help="Chord complexity level")

# Lyrics Template Section
st.divider()
st.subheader("Lyrics Template")
st.caption("Optional structured lyrics for Suno's Lyrics field — controls song structure via bracket tags.")

lyric_col1, lyric_col2 = st.columns([1, 2])

with lyric_col1:
    lyric_keys = list(LYRIC_TEMPLATES.keys())
    lyric_idx = lyric_keys.index(loaded.get("lyric_template", "None")) if loaded.get("lyric_template") in lyric_keys else 0
    lyric_template = st.selectbox("Lyric Template", lyric_keys, index=lyric_idx,
                                  help="Structured fake lyrics that control Suno's song structure. Goes in the Lyrics field, not Style.")

with lyric_col2:
    if lyric_template != "None":
        st.info("This template goes into Suno's **Lyrics** field (separate from Style/Description)")

# API Key and Generation Mode
st.divider()
st.subheader("Generation Settings")

# API Key handling - check env var first, then session state
env_api_key = os.environ.get("OPENAI_API_KEY", "")
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = env_api_key

gen_col1, gen_col2 = st.columns([2, 1])
with gen_col1:
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=st.session_state["openai_api_key"],
        type="password",
        help="Required for LLM generation mode. Set OPENAI_API_KEY env var to pre-fill."
    )
    st.session_state["openai_api_key"] = api_key_input

with gen_col2:
    gen_mode = st.radio(
        "Generation Mode",
        ["Static (Fast)", "LLM (Coherent)"],
        horizontal=True,
        help="Static: Fast concatenation. LLM: AI-generated coherent prompts."
    )
    use_llm = gen_mode == "LLM (Coherent)"

replace_guitar = st.checkbox(
    "I will replace the guitar stem",
    value=loaded.get("replace_guitar", False),
    help="Backing track mode: enforces guitar as the only melodic voice. "
         "Use this when you plan to replace Suno's guitar with your own playing."
)

# Current selections dict
current_selections = {
    "style_preset": style_preset,
    "key_signature": key_signature,
    "style_influence": style_influence,
    "tempo": tempo,
    "mood": mood,
    "intro": intro,
    "progression": progression,
    "harmonic_rhythm": harmonic_rhythm,
    "extensions": extensions,
    "lyric_template": lyric_template,
    "replace_guitar": replace_guitar
}

# Clear refined prompt if selections changed (so refiner uses current prompt)
if "last_selections" in st.session_state:
    if st.session_state["last_selections"] != current_selections:
        # Selections changed - clear old refined prompt
        if "refined_prompt" in st.session_state:
            del st.session_state["refined_prompt"]
        if "refine_score" in st.session_state:
            del st.session_state["refine_score"]
        if "refine_reasoning" in st.session_state:
            del st.session_state["refine_reasoning"]
st.session_state["last_selections"] = current_selections.copy()

# Auto-generate song title from selections (max 80 chars)
def build_auto_title(selections, max_len=80):
    parts = [v for k, v in selections.items() if v != "None" and not isinstance(v, bool)]
    if not parts:
        return "Default Jazz"
    title = " | ".join(parts)
    if len(title) <= max_len:
        return title
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

# Track if we used LLM and if it was cached
llm_used = False
llm_cached = False

if use_llm:
    if st.session_state.get("openai_api_key"):
        with st.spinner("Generating coherent prompt..."):
            try:
                result = generate_prompt(current_selections, st.session_state["openai_api_key"])
                prompt = result["prompt"]
                llm_used = True
                llm_cached = result["cached"]
            except Exception as e:
                st.error(f"LLM generation failed: {e}. Falling back to static.")
                prompt = build_prompt(
                    style_preset=style_preset,
                    key_signature=KEY_SIGNATURES[key_signature],
                    style_influence=STYLE_INFLUENCES[style_influence],
                    tempo=TEMPO_VARIATIONS[tempo],
                    mood=MOOD_VARIATIONS[mood],
                    intro=INTRO_VARIATIONS[intro],
                    progression=PROGRESSION_TYPES[progression],
                    harmonic_rhythm=HARMONIC_RHYTHM[harmonic_rhythm],
                    extensions=CHORD_EXTENSIONS[extensions],
                    replace_guitar=replace_guitar
                )
    else:
        st.warning("Enter OpenAI API key above for LLM generation")
        prompt = build_prompt(
            style_preset=style_preset,
            key_signature=KEY_SIGNATURES[key_signature],
            style_influence=STYLE_INFLUENCES[style_influence],
            tempo=TEMPO_VARIATIONS[tempo],
            mood=MOOD_VARIATIONS[mood],
            intro=INTRO_VARIATIONS[intro],
            progression=PROGRESSION_TYPES[progression],
            harmonic_rhythm=HARMONIC_RHYTHM[harmonic_rhythm],
            extensions=CHORD_EXTENSIONS[extensions]
        )
else:
    prompt = build_prompt(
        style_preset=style_preset,
        key_signature=KEY_SIGNATURES[key_signature],
        style_influence=STYLE_INFLUENCES[style_influence],
        tempo=TEMPO_VARIATIONS[tempo],
        mood=MOOD_VARIATIONS[mood],
        intro=INTRO_VARIATIONS[intro],
        progression=PROGRESSION_TYPES[progression],
        harmonic_rhythm=HARMONIC_RHYTHM[harmonic_rhythm],
        extensions=CHORD_EXTENSIONS[extensions],
        replace_guitar=replace_guitar
    )

# Resolve lyrics template (always static, never LLM-modified)
lyrics_text = LYRIC_TEMPLATES.get(lyric_template, "")

# Show header with generation info
header_text = "Generated Prompt"
if llm_used:
    header_text += " (LLM)"
    if llm_cached:
        header_text += " - Cached"
st.subheader(header_text)

st.markdown("**Style / Description** (paste into Suno's Style field)")
st.text_area("", prompt, height=150, label_visibility="collapsed")

if lyrics_text:
    st.markdown("**Lyrics** (paste into Suno's Lyrics field)")
    st.text_area("", lyrics_text, height=300, key="lyrics_display", disabled=True,
                 label_visibility="collapsed")

# Save button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("Save Song", type="primary"):
        save_song(song_title or "Untitled", current_selections, prompt, lyrics=lyrics_text)
        st.success("Song saved!")
        st.rerun()

# AI Prompt Refiner Agent Section
st.divider()
st.subheader("AI Prompt Refiner Agent")

refine_col1, refine_col2 = st.columns([1, 4])
with refine_col1:
    refine_button = st.button("Refine with Agent")
with refine_col2:
    st.caption(f"Will refine: {prompt[:60]}..." if len(prompt) > 60 else f"Will refine: {prompt}")

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
                st.session_state["refined_prompt"],
                lyrics=lyrics_text
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
                # Style preset always gets a value (no None option)
                if param == "style_preset":
                    batch_selections[param] = random.choice(list(options.keys()))
                else:
                    # Random selection (skip "None" for variety, 20% chance of None)
                    keys = list(options.keys())
                    if random.random() < 0.2:
                        batch_selections[param] = "None"
                    else:
                        non_none = [k for k in keys if k != "None"]
                        batch_selections[param] = random.choice(non_none) if non_none else "None"

        # Carry over the replace_guitar toggle (not randomized)
        batch_selections["replace_guitar"] = replace_guitar

        # Build prompt for this variation
        batch_prompt = build_prompt(
            style_preset=batch_selections["style_preset"],
            key_signature=KEY_SIGNATURES.get(batch_selections["key_signature"], ""),
            style_influence=STYLE_INFLUENCES.get(batch_selections["style_influence"], ""),
            tempo=TEMPO_VARIATIONS[batch_selections["tempo"]],
            mood=MOOD_VARIATIONS[batch_selections["mood"]],
            intro=INTRO_VARIATIONS[batch_selections["intro"]],
            progression=PROGRESSION_TYPES.get(batch_selections["progression"], ""),
            harmonic_rhythm=HARMONIC_RHYTHM.get(batch_selections["harmonic_rhythm"], ""),
            extensions=CHORD_EXTENSIONS.get(batch_selections["extensions"], ""),
            replace_guitar=replace_guitar
        )

        # Resolve lyrics for this batch variation
        batch_lyrics = LYRIC_TEMPLATES.get(batch_selections.get("lyric_template", "None"), "")

        batch_title = build_auto_title(batch_selections)
        batch_results.append({
            "title": batch_title,
            "selections": batch_selections,
            "prompt": batch_prompt,
            "lyrics": batch_lyrics
        })

    st.session_state["batch_results"] = batch_results

# Display batch results
if "batch_results" in st.session_state and st.session_state["batch_results"]:
    st.write("**Generated Variations:**")

    for i, result in enumerate(st.session_state["batch_results"]):
        with st.expander(f"{i+1}. {result['title'][:60]}..."):
            st.text_area("Prompt", result["prompt"], height=100, key=f"batch_prompt_{i}")
            if result.get("lyrics"):
                st.text_area("Lyrics", result["lyrics"], height=150, key=f"batch_lyrics_{i}",
                             disabled=True)
            if st.button("Save This Variation", key=f"save_batch_{i}"):
                save_song(result["title"], result["selections"], result["prompt"],
                          lyrics=result.get("lyrics", ""))
                st.success("Saved!")
                st.rerun()

    # Export batch to CSV
    if st.button("Export Batch to CSV"):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Title", "Style Preset", "Key", "Style Influence",
                       "Tempo", "Mood", "Intro", "Progression", "Harmonic Rhythm", "Extensions",
                       "Lyric Template", "Prompt", "Lyrics"])
        for result in st.session_state["batch_results"]:
            s = result["selections"]
            writer.writerow([
                result["title"],
                s.get("style_preset", ""), s.get("key_signature", ""), s.get("style_influence", ""),
                s.get("tempo", ""), s.get("mood", ""), s.get("intro", ""),
                s.get("progression", ""), s.get("harmonic_rhythm", ""), s.get("extensions", ""),
                s.get("lyric_template", ""),
                result["prompt"],
                result.get("lyrics", "")
            ])
        st.download_button(
            "Download Batch CSV",
            output.getvalue(),
            file_name="suno_batch.csv",
            mime="text/csv"
        )
