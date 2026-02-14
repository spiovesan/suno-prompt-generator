# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Suno Prompt Studio** is a unified Streamlit application for generating Style and Lyrics fields for Suno AI music generation. It combines jazz-specific features with universal genre support.

## Repository Structure

```
suno/
├── app.py              # Main Streamlit application
├── data.py             # All data dictionaries (genres, keys, modes, presets, etc.)
├── generator.py        # Unified generation logic (Jazz + Universal)
├── refiner.py          # AI-powered refinement agent
├── refiner_tools.py    # Tool definitions for refiner
├── knowledge.py        # Knowledge base for best practices
├── storage.py          # Song history persistence
├── cache.py            # LLM response caching
│
├── prompt_generator/   # DEPRECATED - legacy jazz prompt generator
├── workflow_builder/   # DEPRECATED - legacy workflow builder
│
├── docs/               # Documentation and reference materials
│   ├── suno_workflow.md
│   └── ...
│
├── requirements.txt
├── CLAUDE.md
└── README.md
```

## Common Commands

**Run the application:**
```bash
streamlit run app.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Activate virtual environment:**
```bash
source .venv/bin/activate
```

## Architecture

The application follows a modular architecture:

- **data.py**: All configuration dictionaries
  - `GENRES` - Genre list with Jazz first for conditional UI
  - `STYLE_PRESETS` - Jazz quartet presets (guitar lead, piano comping)
  - `STYLE_INFLUENCES` - Era/style references
  - `PROGRESSION_TYPES`, `HARMONIC_RHYTHM`, `CHORD_EXTENSIONS` - Jazz harmony options
  - `MAJOR_KEYS`, `MINOR_KEYS`, `MODES` - Universal key/mode options
  - `TIME_SIGNATURES`, `TEMPO_RANGES`, `MOOD_VARIATIONS` - Universal rhythm/mood
  - `SECTION_TYPES`, `DEFAULT_SECTIONS` - Song structure templates
  - `AUDIO_QUALITY_TEMPLATE` - Pro mastering prompt template
  - `LYRIC_TEMPLATES` - Structured song field templates

- **generator.py**: Unified generation logic
  - `generate_outputs()` - Main function returning `{style, lyrics, cached}`
  - Jazz mode: Style presets + optional LLM generation
  - Universal mode: Audio quality template
  - Supports Suno lyrics paste feature

- **refiner.py + refiner_tools.py**: AI-powered refinement
  - Uses OpenAI function calling (gpt-4o-mini)
  - Analyzes and improves both Style and Lyrics outputs
  - Jazz-specific and Universal analysis modes
  - Returns scores and reasoning

- **knowledge.py**: Best practices knowledge base
  - Meta tag guidelines
  - Audio quality guidelines
  - Jazz-specific guidelines

- **storage.py**: Song history persistence (JSON)
- **cache.py**: LLM response caching (JSON)

## Key Features

1. **Genre-Driven UI**: Jazz genre enables jazz-specific options
2. **Dynamic Song Structure**: Add/remove sections with meta tags
3. **Suno Lyrics Paste**: Paste existing Suno lyrics to combine with structure
4. **Dual Output**: Always generates both Style and Lyrics fields
5. **LLM Generation**: Optional AI-powered coherent prompt generation (Jazz)
6. **Replace Guitar Stem**: Mode for creating backing tracks
7. **Song History**: Save/load songs with all settings
8. **Batch Generation**: Generate multiple variations
9. **AI Refinement**: Analyze and improve outputs with AI

## Development Notes

- The app uses conditional UI: Jazz genre shows jazz presets, harmony options
- Other genres use the universal Audio Quality Template for Style field
- Suno bracket tags: `[Intro]`, `[Verse]`, `[Chorus]`, etc.
- Harmony bracket tags: `[ii-V-I progression]`, `[modal vamp]`, etc.
- Jazz mode hard constraints: quartet only (guitar, piano, bass, drums), no artist names
