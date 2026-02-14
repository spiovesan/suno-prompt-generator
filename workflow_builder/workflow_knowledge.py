"""
Knowledge base for Suno Workflow Builder refiner.
Contains best practices for meta tags, audio quality, and song structure.
"""

# Meta tag best practices
META_TAG_GUIDELINES = {
    "general": """
## Meta Tag Best Practices for Suno

- Use square brackets: [Section: instruments, mood]
- Keep descriptors concise: 1-3 elements per tag
- Be specific with instruments and effects
- Match energy levels to section purpose
- Use consistent terminology throughout
""",

    "sections": """
## Section-Specific Guidelines

**[Intro]**: Set the mood, use ambient or sparse instrumentation
- Good: "ambient pads, soft piano", "atmospheric, building"
- Avoid: Starting too full/loud

**[Verse]**: Lower energy than chorus, storytelling focus
- Good: "acoustic guitar, mellow tone", "intimate, sparse"
- Avoid: Overpowering instrumentation

**[Pre-Chorus]**: Build tension, prepare for chorus
- Good: "rising synths, building energy", "anticipation, lift"
- Avoid: Staying flat or dropping energy

**[Chorus]**: Peak energy, memorable hooks
- Good: "full band, high energy", "powerful, anthemic"
- Avoid: Being too similar to verses

**[Bridge]**: Contrast, new perspective
- Good: "synth arpeggios, key change", "stripped back, reflective"
- Avoid: Repeating verse/chorus patterns

**[Drop]**: Maximum impact (EDM/electronic)
- Good: "heavy bass, synth stabs", "massive, crushing"
- Avoid: Building without payoff

**[Outro]**: Resolution, fade or conclusion
- Good: "fade out, ambient", "resolving, gentle"
- Avoid: Abrupt endings without intent
""",

    "instruments": """
## Instrument Descriptors That Work Well

**Electric Instruments:**
- "distorted guitar", "clean electric", "wah guitar"
- "synth pads", "synth arpeggios", "synth bass"
- "Rhodes piano", "wurlitzer", "organ"

**Acoustic Instruments:**
- "acoustic guitar", "nylon guitar", "steel strings"
- "grand piano", "upright piano"
- "strings", "orchestral swells"

**Drums/Percussion:**
- "live drums", "electronic drums", "808s"
- "brushed drums", "punchy kick", "crisp snare"
- "percussion loops", "shakers", "tambourine"

**Bass:**
- "sub bass", "synth bass", "slap bass"
- "walking bass", "groovy bass", "deep bass"

**Modifiers:**
- "ambient", "atmospheric", "lush"
- "gritty", "clean", "distorted"
- "sparse", "full", "layered"
""",

    "transitions": """
## Transition Guidelines

**Building Up:**
- "rising", "building", "crescendo"
- "tension increasing", "anticipation"
- "drums intensifying", "layers adding"

**Breaking Down:**
- "stripped back", "minimal", "sparse"
- "drums drop out", "bass solo"
- "breathing room", "space"

**Maintaining Energy:**
- "driving", "persistent", "steady"
- "locked groove", "momentum"

**Key Changes:**
- "key change up", "modulation"
- "lift", "brightness shift"
""",

    "anti_patterns": """
## Common Mistakes to Avoid

1. **Vague descriptors**: "good sound" → Use specific terms like "warm analog mix"

2. **Conflicting instructions**: "soft, aggressive drums" → Pick one direction

3. **Too many elements**: "[Verse: acoustic guitar, piano, synth pads, strings, brass, drums]"
   → Focus on 2-3 key elements per section

4. **No energy variation**: Same descriptors for every section
   → Build contrast between sections

5. **Generic terms**: "nice melody", "cool beat"
   → Use specific: "arpeggiated synth melody", "four-on-floor kick"

6. **Missing structure flow**: Random section order
   → Follow natural song arc: build → peak → release
"""
}

# Audio quality template guidelines
AUDIO_QUALITY_GUIDELINES = {
    "general": """
## Audio Quality Prompt Best Practices

The audio quality prompt goes in Suno's Style field and affects:
- Mix balance and clarity
- Mastering quality
- Frequency response
- Stereo field and spatial characteristics

Key elements to include:
1. Genre-specific quality descriptors
2. Mix characteristics (balanced highs/mids/lows)
3. Bass treatment (tight, controlled, punchy)
4. Vocal treatment (if applicable)
5. Reverb/space characteristics
6. Mastering specs (-1 dBTP, no pumping)
7. Noise floor quality
""",

    "genre_specific": """
## Genre-Specific Audio Quality Notes

**Electronic/EDM:**
- Emphasize sub-bass control, sidechain
- "festival-ready", "club mix"
- Tight low-end, punchy transients

**Jazz/Acoustic:**
- "warm", "natural", "analog"
- Room sound, live feel
- Less compression, more dynamics

**Pop:**
- Polished, radio-ready
- Vocal-forward mix
- Controlled dynamics

**Rock:**
- Powerful guitars, present drums
- "punchy", "energetic"
- Balanced aggression

**Hip-Hop/Trap:**
- Heavy 808s, crisp hi-hats
- Vocal clarity above bass
- "hard-hitting", "trunk-rattling"

**Lo-fi:**
- Intentional imperfections
- Vinyl texture, warmth
- Soft compression, rounded edges
""",

    "mixing_terms": """
## Effective Mixing Terminology

**Frequency Balance:**
- "well-balanced highs, mids, and lows"
- "carved 200-400 Hz for clarity"
- "8-12 kHz sheen for sparkle"

**Bass:**
- "tight sub-bass, centered and controlled"
- "punchy low-end with clear kick separation"

**Mids:**
- "warm midrange presence, no boxiness"
- "crystal-clear leads"

**Highs:**
- "crisp presence", "smooth air"
- "no harshness", "silky highs"

**Dynamics:**
- "transparent mastering"
- "no pumping on mix bus"
- "sharp transient definition"

**Space/Reverb:**
- "short plate reverb with subtle pre-delay"
- "tight slapback delay"
- "wide stereo field"
"""
}


def get_meta_tag_guidelines(aspect: str) -> str:
    """Get meta tag guidelines for a specific aspect."""
    return META_TAG_GUIDELINES.get(aspect, META_TAG_GUIDELINES.get("general", "No guidelines found."))


def get_audio_quality_guidelines(aspect: str) -> str:
    """Get audio quality guidelines for a specific aspect."""
    return AUDIO_QUALITY_GUIDELINES.get(aspect, AUDIO_QUALITY_GUIDELINES.get("general", "No guidelines found."))


def get_all_guidelines() -> dict:
    """Get all guidelines combined."""
    return {
        "meta_tags": META_TAG_GUIDELINES,
        "audio_quality": AUDIO_QUALITY_GUIDELINES
    }
