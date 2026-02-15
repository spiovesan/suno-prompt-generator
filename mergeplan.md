# Fix: Smart Merge of Pasted Lyrics with Song Structure

## Current Problem

When user pastes lyrics with **fewer sections** than the preset, the auto-sync **replaces** the entire structure:

**Example:**
- User selects Meditation preset: `Intro, Verse, Verse, Bridge, Verse, Outro` (6 sections)
- User pastes lyrics with only: `[Verse]` and `[Chorus]` (2 sections)
- **Current behavior**: Structure replaced with only 2 sections (Verse, Chorus)
- **Desired behavior**: Keep all 6 sections, map lyrics to matching sections

## Desired "UNION" Behavior

1. **Keep preset structure** - Don't shrink when lyrics have fewer sections
2. **Map lyrics to sections** - [Verse] lyrics apply to ALL Verse sections in structure
3. **Instrumental sections** - Sections without matching lyrics (Intro, Bridge, Outro) stay instrumental
4. **Add missing types** - If lyrics have [Chorus] but structure doesn't, add it
5. **Repeat with variations** - If 3 Verses but 1 Verse lyrics, repeat (output already does this)

## Root Cause

The auto-sync in `app.py` (lines 489-507) completely **replaces** `st.session_state.sections` with parsed lyrics sections:

```python
parsed_sections = parse_lyrics_to_sections(current_lyrics)
st.session_state.sections = parsed_sections  # REPLACES entire structure!
```

## Solution: Smart Merge with User Preference

### User Choices:
- **Missing section types**: Replace nearest match (map [Chorus] to closest section like Verse)
- **Sync behavior**: Full merge (keep structure + add missing types + preserve instruments)

### New Logic:

```
CURRENT STRUCTURE: [Intro, Verse, Verse, Bridge, Verse, Outro] (6 sections)
PASTED LYRICS:     [Verse] "line 1", [Chorus] "line 2"

MERGE RESULT:
1. Keep all 6 preset sections
2. [Verse] lyrics → applies to all 3 Verse sections (repeated)
3. [Chorus] has no match → map to nearest (Bridge) OR add Chorus section
4. Intro, Outro → stay instrumental (no matching lyrics)
```

---

## Implementation Plan

### Files to Modify

| File | Changes |
|------|---------|
| `app.py` | Add merge preference option, modify auto-sync to MERGE instead of REPLACE |
| `generator.py` | Update `_build_lyrics_output` to handle "nearest match" mapping |

### Step 0: Add Merge Preference Option (app.py sidebar)

Add a selectbox in the sidebar to let user choose merge behavior:

```python
# In sidebar, after "Auto-fill section instruments" checkbox
st.selectbox(
    "Lyrics sync mode",
    options=["Smart merge", "Replace structure", "Keep structure"],
    index=0,  # Default: Smart merge
    key="lyrics_sync_mode",
    help="""
    • Smart merge: Keep preset + add missing section types from lyrics
    • Replace structure: Lyrics completely replace song structure
    • Keep structure: Never modify structure, just map lyrics at output
    """
)
```

### Step 1: Change Auto-Sync Based on Preference (app.py ~line 489-510)

Update the sync logic to respect the user's preference:

```python
# Only sync if lyrics changed AND have section tags
if current_lyrics != st.session_state.prev_lyrics:
    if current_lyrics.strip() and "[" in current_lyrics:
        sync_mode = st.session_state.get("lyrics_sync_mode", "Smart merge")

        # "Keep structure" mode - don't modify structure at all
        if sync_mode == "Keep structure":
            st.session_state.prev_lyrics = current_lyrics
            # Don't modify sections - lyrics will be mapped at output time

        from generator import parse_lyrics_to_sections, suggest_section_instruments
        parsed_sections = parse_lyrics_to_sections(current_lyrics)

        if parsed_sections and len(parsed_sections) > 0:

            # "Replace structure" mode - current behavior
            if sync_mode == "Replace structure":
                if st.session_state.get("auto_fill_sections", True):
                    current_genre = st.session_state.get("genre_select", "default")
                    current_mood = st.session_state.get("mood_select", "default")
                    parsed_sections = suggest_section_instruments(
                        sections=parsed_sections,
                        genre=current_genre,
                        mood=current_mood
                    )
                st.session_state.sections = parsed_sections
                st.session_state.prev_lyrics = current_lyrics
                st.toast(f"Synced {len(parsed_sections)} sections from lyrics")
                st.rerun()

            # "Smart merge" mode - keep structure + add missing types
            elif sync_mode == "Smart merge":
                current_sections = [s.copy() for s in st.session_state.sections]

                # Get unique section types
                lyrics_types = set(s['type'].lower() for s in parsed_sections)
                current_types = set(s['type'].lower() for s in current_sections)

                # Find section types in lyrics but NOT in current structure
                missing_types = lyrics_types - current_types
                added_count = 0

                # Add missing types at appropriate positions
                if missing_types:
                    for parsed in parsed_sections:
                        ptype = parsed['type'].lower()
                        if ptype in missing_types:
                            # Find best insertion point
                            insert_idx = _find_insert_position(current_sections, parsed['type'])
                            new_section = create_section(parsed['type'], parsed.get('instruments', ''))
                            current_sections.insert(insert_idx, new_section)
                            missing_types.discard(ptype)
                            added_count += 1

                # Auto-fill instruments for new sections
                if added_count > 0 and st.session_state.get("auto_fill_sections", True):
                    current_genre = st.session_state.get("genre_select", "default")
                    current_mood = st.session_state.get("mood_select", "default")
                    current_sections = suggest_section_instruments(
                        sections=current_sections,
                        genre=current_genre,
                        mood=current_mood
                    )

                st.session_state.sections = current_sections
                st.session_state.prev_lyrics = current_lyrics

                if added_count > 0:
                    st.toast(f"Added {added_count} section type(s) from lyrics")
                    st.rerun()

    st.session_state.prev_lyrics = current_lyrics
```

### Step 2: Add Helper Function (app.py)

```python
def _find_insert_position(sections: list, new_type: str) -> int:
    """Find best position to insert a new section type."""
    new_type_lower = new_type.lower()

    # Section type ordering preference
    TYPE_ORDER = ["intro", "verse", "pre-chorus", "chorus", "post-chorus",
                  "bridge", "breakdown", "buildup", "drop", "solo",
                  "interlude", "outro"]

    try:
        new_order = TYPE_ORDER.index(new_type_lower)
    except ValueError:
        return len(sections)  # Unknown type goes at end

    # Find first section that should come after new_type
    for i, s in enumerate(sections):
        try:
            existing_order = TYPE_ORDER.index(s['type'].lower())
            if existing_order > new_order:
                return i
        except ValueError:
            continue

    return len(sections)  # Add at end if no suitable position
```

### Step 3: Update Output Merge Logic (generator.py ~line 623-636)

Add fallback mapping for unmatched lyrics:

```python
def _get_nearest_section_type(section_type: str, available_types: set) -> str:
    """Find nearest matching section type for unmapped lyrics."""
    section_type = section_type.lower()

    # Direct mappings for common pairs
    SIMILAR_SECTIONS = {
        "chorus": ["verse", "hook", "refrain"],
        "pre-chorus": ["verse", "bridge"],
        "post-chorus": ["chorus", "verse"],
        "hook": ["chorus", "verse"],
        "refrain": ["chorus"],
        "interlude": ["bridge", "breakdown"],
    }

    # Try similar types first
    if section_type in SIMILAR_SECTIONS:
        for similar in SIMILAR_SECTIONS[section_type]:
            if similar in available_types:
                return similar

    # Fallback: return first available lyrical section
    for fallback in ["verse", "chorus", "bridge"]:
        if fallback in available_types:
            return fallback

    return None  # No suitable match - leave as instrumental
```

Then in `_build_lyrics_output`, after the direct match check:

```python
# Try to find matching lyrics for this section type
section_key = section_type.lower()
if section_key in parsed_lyrics:
    # ... existing matching logic ...
elif parsed_lyrics:
    # No direct match - try nearest section type
    nearest = _get_nearest_section_type(section_key, set(parsed_lyrics.keys()))
    if nearest and nearest in parsed_lyrics:
        # Use lyrics from nearest matching type
        counter = section_counters.get(nearest, 0)
        lyrics_list = parsed_lyrics[nearest]
        if counter < len(lyrics_list):
            lines.append(lyrics_list[counter])
            section_counters[nearest] = counter + 1
        elif lyrics_list:
            lines.append(lyrics_list[-1])
```

---

## Verification

### Test 1: Smart Merge Mode (Default)
1. Set "Lyrics sync mode" to "Smart merge"
2. Select Meditation preset (6 sections: Intro, Verse, Verse, Bridge, Verse, Outro)
3. Paste lyrics with only `[Verse]` and `[Chorus]`
4. **Expected**:
   - Structure becomes 7 sections (Chorus added after Verse)
   - Existing instruments preserved
   - Toast: "Added 1 section type(s) from lyrics"
5. Click Generate
6. **Expected output**:
   - [Verse] lyrics repeated across all 3 Verse sections
   - [Chorus] lyrics appear in Chorus section
   - Intro, Bridge, Outro are instrumental

### Test 2: Replace Structure Mode
1. Set "Lyrics sync mode" to "Replace structure"
2. Load any preset
3. Paste lyrics with `[Verse]` and `[Chorus]`
4. **Expected**: Structure replaced with only 2 sections (current behavior)

### Test 3: Keep Structure Mode
1. Set "Lyrics sync mode" to "Keep structure"
2. Load preset with 6 sections
3. Paste lyrics with only `[Verse]`
4. **Expected**: Structure unchanged (still 6 sections)
5. Click Generate
6. **Expected output**: [Verse] lyrics mapped to Verse sections, others instrumental

### Test 4: Instruments Preserved
1. Load preset, note the auto-filled instruments
2. Paste lyrics
3. **Expected**: Existing instruments not wiped out
