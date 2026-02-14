"""
Music theory data for Suno Workflow Builder.
Based on suno_workflow.md specifications.
"""

# Major keys with emotional descriptions and genre associations
MAJOR_KEYS = {
    "C Major": "Pure, open, neutral, balanced (clean pop, folk, beginner-friendly)",
    "G Major": "Warm, natural, uplifting (country, Americana, classic rock)",
    "D Major": "Triumphant, regal, bold (orchestral, rock ballads, anthemic)",
    "A Major": "Bright, confident, joyful (pop rock, upbeat country, singalongs)",
    "E Major": "Brash, energetic, exciting (rock, blues, aggressive pop)",
    "B Major": "Radiant, assertive, polished (gospel, R&B, cinematic)",
    "F Major": "Pastoral, calm, gentle (classical, singer-songwriter, soft rock)",
    "Bb Major": "Noble, rich, full (jazz, brass-heavy arrangements, classical)",
    "Eb Major": "Lush, mellow, expressive (soul, funk, ballads)",
}

# Minor keys with emotional descriptions and genre associations
MINOR_KEYS = {
    "A Minor": "Sad, introspective, sincere (acoustic ballads, emo, lo-fi)",
    "E Minor": "Haunting, melancholic, mysterious (metal, alt rock, cinematic)",
    "D Minor": "Dramatic, tragic, emotional (classical, folk noir, film scoring)",
    "B Minor": "Dark, brooding, poetic (indie, alt-pop, gothic rock)",
    "F# Minor": "Tense, sorrowful, expressive (experimental, downbeat pop, EDM)",
    "C# Minor": "Ethereal, romantic, haunting (dream pop, ambient, solo piano)",
    "G Minor": "Bold, mournful, stormy (classical, jazz, moody pop)",
}

# Musical modes with mood and genre associations
MODES = {
    "Ionian (Major)": {
        "mood": "Bright, happy, stable",
        "feel": "Optimistic, confident",
        "genres": "Pop, country, classical, folk, children's music",
    },
    "Dorian": {
        "mood": "Cool, soulful, moody but hopeful",
        "feel": "A minor scale with a jazzy or gospel uplift",
        "genres": "Funk, soul, gospel, R&B, jazz, Celtic folk",
    },
    "Phrygian": {
        "mood": "Dark, exotic, tense",
        "feel": "Intense, dramatic",
        "genres": "Flamenco, metal, Middle Eastern, Spanish-influenced",
    },
    "Lydian": {
        "mood": "Dreamy, ethereal, expansive",
        "feel": "Bright but floaty, surreal",
        "genres": "Film scores, dream pop, progressive rock, fusion",
    },
    "Mixolydian": {
        "mood": "Gritty, bluesy, relaxed confidence",
        "feel": "Like major, but more swagger",
        "genres": "Blues, rock, country, funk, jam band music",
    },
    "Aeolian (Minor)": {
        "mood": "Sad, introspective, dramatic",
        "feel": "Classic minor feel with emotional pull",
        "genres": "Alt rock, ballads, EDM, cinematic, folk",
    },
    "Locrian": {
        "mood": "Unsettling, chaotic, unresolved",
        "feel": "Darkest mode, diminished tonic makes it unstable",
        "genres": "Experimental, avant-garde, some black metal",
    },
}

# Time signatures with feel descriptions
TIME_SIGNATURES = {
    "4/4": "Standard, driving, marching (most common)",
    "3/4": "Waltz, flowing, romantic",
    "6/8": "Rolling, compound, shuffle feel",
    "2/4": "March, polka, rapid-fire",
    "12/8": "Swinging triplets, soulful, gospel groove",
    "5/4": "Odd, progressive, unsettling",
    "7/8": "Complex, prog rock, asymmetric",
}

# Tempo ranges with phrasing hints
TEMPO_RANGES = {
    "Slow (60-80 BPM)": "Intimate, meditative, slow-burning",
    "Mid-tempo (80-110 BPM)": "Groovy, versatile, laid-back groove",
    "Upbeat (110-130 BPM)": "Energetic, punchy and upbeat, driving rhythm",
    "Fast (130+ BPM)": "High energy, dance, urgency",
}

# Common genres for the audio quality template
GENRES = [
    "Lo-fi",
    "Pop",
    "Rock",
    "Hip-Hop",
    "R&B",
    "Jazz",
    "Electronic",
    "EDM",
    "House",
    "Techno",
    "Ambient",
    "Classical",
    "Country",
    "Folk",
    "Metal",
    "Indie",
    "Soul",
    "Funk",
    "Reggae",
    "Blues",
    "Trap",
    "Drill",
    "Future Bass",
    "Big Room Trance",
    "Progressive House",
    "Synthwave",
    "Cinematic",
]

# Song section types for meta tags
SECTION_TYPES = [
    "Intro",
    "Verse",
    "Pre-Chorus",
    "Chorus",
    "Post-Chorus",
    "Bridge",
    "Breakdown",
    "Buildup",
    "Drop",
    "Solo",
    "Outro",
    "Coda",
]

# Poetic meters for lyrics guidance
POETIC_METERS = {
    "Iamb (da-DUM)": {
        "pattern": "da-DUM",
        "example": "I walked alone beneath the sky",
        "feel": "Smooth, natural",
        "genres": "Pop, folk, ballads",
    },
    "Trochee (DA-dum)": {
        "pattern": "DA-dum",
        "example": "Shadows fall on ruined stone",
        "feel": "Forceful, chant-like",
        "genres": "Rock, gothic, chanty hooks",
    },
    "Anapest (da-da-DUM)": {
        "pattern": "da-da-DUM",
        "example": "In the dead of the night, I was gone",
        "feel": "Flowing, builds momentum",
        "genres": "Rap, gospel, theatrical",
    },
    "Dactyl (DA-da-dum)": {
        "pattern": "DA-da-dum",
        "example": "Memories fade away from me",
        "feel": "Rolling, dramatic",
        "genres": "6/8 or 12/8 feel songs",
    },
    "Amphibrach (da-DUM-da)": {
        "pattern": "da-DUM-da",
        "example": "I walked along the ruins",
        "feel": "Balanced yet flowing",
        "genres": "3/4 or 9/8 feels",
    },
}

# Audio quality template - genre gets inserted at {genre}
AUDIO_QUALITY_TEMPLATE = """{genre} audio quality:
studio quality, fully mastered
well-balanced highs, mids, and lows
tight sub-bass, centered and controlled
punchy low-end with clear kick separation
warm midrange presence, no boxiness
crystal-clear leads, minimal reverb, no muddy mix
vocals upfront and natural, crisp presence with smooth air
light de-ess on sibilance, gentle saturation only
short plate reverb with subtle pre-delay, tight slapback delay for space
double/triple vocal stacks low in mix, clear diction, no over-tuning
sidechain preserves vocal transients; sub energy never masks vocals
carved 200–400 Hz for clarity, added 8–12 kHz sheen for sparkle
dry and polished vocal sound, controlled reverb, sharp transient definition, no distortion
festival-ready, cinematic, wide stereo field, energetic club mix
transparent mastering with -1 dBTP ceiling, no pumping on mix bus
spotless noise floor, no hiss, no artifacts"""

# Default section suggestions per genre
DEFAULT_SECTIONS = {
    "Pop": ["Intro", "Verse", "Pre-Chorus", "Chorus", "Verse", "Chorus", "Bridge", "Chorus", "Outro"],
    "Rock": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Solo", "Chorus", "Outro"],
    "EDM": ["Intro", "Buildup", "Drop", "Breakdown", "Buildup", "Drop", "Outro"],
    "Hip-Hop": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Verse", "Outro"],
    "Jazz": ["Intro", "Verse", "Solo", "Verse", "Solo", "Outro"],
    "default": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Bridge", "Chorus", "Outro"],
}
