# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based web application that generates music prompts for Suno AI. It allows users to customize jazz music characteristics through various parameters (tonality, mode family, guitar style, groove) and generates a formatted prompt string.

## Architecture

The codebase follows a simple three-module architecture:

- **app.py**: Streamlit UI layer - handles user interface with selectboxes for musical parameters and displays generated prompts
- **prompt_engine.py**: Core logic for building prompt strings by concatenating base prompt with selected variations
- **data.py**: Configuration module containing BASE_PROMPT template and all musical variation dictionaries (TONALITY_MODES, MODE_FAMILIES, GUITAR_VARIATIONS, GROOVE_VARIATIONS)

The data flow is: UI selections → prompt_engine.build_prompt() → concatenated string output

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

## Development Notes

- When adding new musical variations, update the corresponding dictionary in data.py
- The build_prompt() function filters out empty strings, so "None" options map to empty strings
- The BASE_PROMPT in data.py defines the foundational musical style; all variations are appended to it
