"""
Unified data for Suno Prompt Studio.
Combines prompt_generator (jazz-specific) and workflow_builder (universal) data.
"""

# =============================================================================
# GENRES - Jazz first for conditional UI
# =============================================================================
GENRES = [
    "Jazz",  # First for jazz-specific features
    "Lo-fi",
    "Pop",
    "Rock",
    "Hip-Hop",
    "R&B",
    "Electronic",
    "EDM",
    "House",
    "Techno",
    "Ambient",
    "Meditation",  # Healing, relaxation, spa music
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

# =============================================================================
# JAZZ-SPECIFIC (from prompt_generator)
# =============================================================================

# Jazz style presets - strictly quartet: guitar (lead), piano (comping), bass, drums
STYLE_PRESETS = {
    "Smooth Jazz": (
        "smooth jazz quartet, jazz guitar lead melody, "
        "clean hollow-body guitar solo, Rhodes piano comping behind, "
        "groovy electric bass, brushed drums, "
        "guitar plays the theme, piano supports with 9th and 13th chord voicings, "
        "guitar-led instrumental"
    ),
    "Bebop": (
        "bebop jazz quartet, bebop guitar lead lines, "
        "virtuosic guitar runs and arpeggios, piano comping with altered dominants, "
        "walking upright bass, crisp snare, "
        "guitar plays head and solos, piano accompaniment, "
        "fast ii-V-I progressions, guitar-led instrumental"
    ),
    "Modal Jazz": (
        "modal jazz quartet, expressive guitar lead, "
        "warm jazz guitar melody with sustain, piano pads with sus4 and add9 chords, "
        "pedal bass tones, contemplative drums, "
        "guitar carries the theme, piano provides quartal voicing support, "
        "Dorian mode, guitar-led instrumental"
    ),
    "Jazz Fusion": (
        "jazz fusion quartet, distorted guitar lead, "
        "electric guitar solos with wah and delay, synth piano layers behind, "
        "funky slap bass, powerful drums, "
        "guitar is featured soloist, piano comps polychords, "
        "lydian dominant, guitar-led instrumental"
    ),
    "Latin Jazz": (
        "latin jazz quartet, nylon guitar lead melody, "
        "flamenco-tinged guitar runs, montuno piano comping, "
        "syncopated bass, energetic drums and percussion, "
        "guitar plays theme and improvises, piano supports with maj7#11 voicings, "
        "Afro-Cuban feel, guitar-led instrumental"
    ),
    "Cool Jazz": (
        "cool jazz quartet, mellow guitar lead, "
        "relaxed jazz guitar tone with light vibrato, piano comping with rootless voicings, "
        "understated bass, gentle swing drums, "
        "guitar states melody, piano fills harmonically, "
        "smooth voice leading, guitar-led instrumental"
    ),
    "Hard Bop": (
        "hard bop quartet, bluesy guitar lead, "
        "punchy guitar riffs with blues bends, soulful piano comping, "
        "driving bass, gospel-influenced drums, "
        "guitar leads with attitude, piano responds with gospel voicings, "
        "dominant 7#9 feel, guitar-led instrumental"
    ),
    "Post-Bop": (
        "post-bop quartet, angular guitar lead, "
        "adventurous guitar lines with chromatic runs, piano voicings underneath, "
        "fluid bass lines, polyrhythmic drums, "
        "guitar explores complex harmonic cycles, piano supports with superimposed triads,"
        "guitar-led instrumental"
    ),
    "Acid Jazz": (
        "acid jazz quartet, wah guitar lead, "
        "funky guitar riffs with wah pedal, organ and Rhodes comping, "
        "deep electric bass groove, breakbeat drums, "
        "guitar drives the groove, keyboard supports with 9th chords, "
        "guitar-led instrumental"
    ),
    "ECM Style": (
        "ECM records style quartet, ambient guitar lead, "
        "clean guitar with reverb and volume swells, spacious piano textures, "
        "minimalist bass, subtle drums, "
        "guitar creates atmosphere and melody, piano adds open voicings, "
        "quartal harmony, guitar-led instrumental"
    ),
    "Contemporary Chamber Jazz": (
        "Instrumental only, no vocals. Contemporary chamber jazz and modern improvised music "
        "with ECM-like and post-tonal aesthetics. Focus on vertical harmony, intervallic structures "
        "and harmonic fields instead of functional progressions. Steady tempo without groove repetition, "
        "no swing or fusion cliches. Clean electric guitar as primary voice, switching briefly to "
        "restrained lead guitar during the solo, then returning clean. Music is intentionally "
        "non-soothing, non-background, with persistent harmonic tension and no tonal resolution."
    ),
    "Post-Tonal Improvised": (
        "Instrumental only, no vocals. Post-tonal improvised music influenced by contemporary "
        "classical language and modern jazz abstraction. Emphasis on non-functional harmony, "
        "chromatic instability and asymmetric phrasing rather than themes or grooves. Rhythm section "
        "avoids repetition and supports harmonic instability. Guitar is used as a textural and "
        "intervallic instrument, becoming a restrained lead voice only in the solo before returning "
        "to clean texture. Intentionally anti-listening and resistant to passive enjoyment."
    ),
    "Radical Anti-Listening": (
        "Instrumental only, no vocals. Radical anti-listening music that resists comfort, "
        "memorability and tonal grounding. Harmony treated as unstable vertical blocks rather than "
        "progressions, avoiding triadic and functional motion. No groove repetition, no lyrical themes, "
        "no cinematic or fusion traits. Clean electric guitar used dry and unsweetened, briefly shifting "
        "to restrained lead guitar during the solo, then returning clean. Music remains unresolved, "
        "uncomfortable and non-functional by design."
    ),
}

# Keep original for backwards compatibility
BASE_PROMPT = STYLE_PRESETS["Smooth Jazz"]

# Jazz style influences - guitar as lead focus
STYLE_INFLUENCES = {
    "None": "",
    "1959 Modal Cool": "late 50s modal jazz, guitar plays So What theme, quartal harmony, spacious guitar phrasing",
    "70s Electric Funk Jazz": "1970s electric jazz funk, guitar wah riffs lead, chromatic bass, extended 9th chords",
    "Lyrical Guitar Landscapes": "lyrical jazz guitar melodies, singing guitar tone, open add9 voicings, Lydian warmth",
    "World Fusion Synths": "jazz fusion with world rhythms, guitar explores unusual scales, polychordal piano support",
    "Impressionist Harmony": "impressionistic feel, guitar with parallel chord movement, whole tone colors, dreamy",
    "Spiritual Intensity": "spiritual jazz, searching guitar improvisation, sus4 resolutions, transcendent building",
    "Latin Fusion Virtuoso": "virtuosic Latin fusion, fast guitar runs, altered dominants, flamenco-tinged",
    "Solo Guitar Focus": "solo guitar featured, rubato phrasing, rich chord melody, classical-jazz hybrid",
    "Modern Collective Groove": "modern fusion, interlocking grooves, guitar and piano trading, slash chords",
    "Neo-Soul Jazz": "neo-soul jazz, smooth guitar lead, minor 9th vamps, Rhodes support, laid-back",
    "Contemporary Guitar Trio": "contemporary guitar trio feel, melodic guitar, flowing ninths, conversational",
    "Guitar-Piano Dialogue": "conversational guitar and piano, guitar leads phrases, piano responds harmonically",
    "Lyrical Melodic": "lyrical guitar sound, bright tone, melodic development, orchestral guitar approach",
    "Gritty Blues-Funk": "gritty guitar tone, bluesy bends, funky comping, raw energy guitar lead",
}


def get_genre_preset_names(genre: str) -> dict:
    """
    Get style preset names adapted to the selected genre.

    For Jazz, returns original names.
    For other genres, replaces "Jazz" with the genre name.

    Example: "Smooth Jazz" → "Smooth Ambient" when genre is Ambient
    """
    if genre == "Jazz":
        return STYLE_PRESETS

    adapted = {}
    for name, value in STYLE_PRESETS.items():
        # Replace "Jazz" with genre name in preset names
        if "Jazz" in name:
            new_name = name.replace("Jazz", genre)
        else:
            # For names without "Jazz" (like "Bebop"), append genre
            new_name = f"{name} {genre}"
        adapted[new_name] = value

    return adapted


def resolve_preset_value(preset_name: str, genre: str) -> str:
    """
    Resolve a preset name to its value, handling genre-adapted names.

    Args:
        preset_name: The display name (may be genre-adapted like "Smooth Rock")
        genre: The current genre

    Returns:
        The preset value/description
    """
    # If it's an original preset name, use directly
    if preset_name in STYLE_PRESETS:
        return STYLE_PRESETS[preset_name]

    # Otherwise, get the adapted dict and look up
    adapted = get_genre_preset_names(genre)
    if preset_name in adapted:
        return adapted[preset_name]

    # Fallback to first preset
    return list(STYLE_PRESETS.values())[0]


def resolve_influence_value(influence_name: str, genre: str) -> str:
    """
    Resolve an influence name to its value, handling genre-adapted names.

    Args:
        influence_name: The display name
        genre: The current genre

    Returns:
        The influence value/description
    """
    # Get the appropriate influences dict for the genre
    influences = get_genre_influence_names(genre)
    if influence_name in influences:
        return influences[influence_name]

    # Fallback
    return ""


def get_genre_influence_names(genre: str) -> dict:
    """
    Get style influence names adapted to the selected genre.

    For Jazz, returns original jazz-specific influences.
    For other genres, returns universal influences that work across genres.
    """
    if genre == "Jazz":
        return STYLE_INFLUENCES

    # Universal influences that work for any genre
    universal_influences = {
        "None": "",
        "1959 Modal Cool": "modal harmony, quartal voicings, spacious phrasing",
        "70s Electric Funk": "1970s electric funk, wah riffs, chromatic bass, extended 9th chords",
        "Lyrical Melodic": "lyrical melodies, singing tone, open voicings, warm harmonics",
        "World Fusion": "world fusion rhythms, unusual scales, polychordal support",
        "Impressionist Harmony": "impressionistic feel, parallel chord movement, whole tone colors, dreamy",
        "Spiritual Intensity": "spiritual intensity, searching improvisation, transcendent building",
        "Latin Virtuoso": "virtuosic Latin influence, fast runs, altered dominants",
        "Solo Featured": "solo instrument featured, rubato phrasing, rich voicings",
        "Modern Collective": "modern collective groove, interlocking parts, slash chords",
        "Neo-Soul Smooth": "neo-soul influence, smooth lead, minor 9th vamps, laid-back",
        "Contemporary Trio": "contemporary trio feel, melodic, flowing ninths, conversational",
        "Dialogue Style": "conversational style, call and response, harmonic interplay",
        "Gritty Blues-Funk": "gritty tone, bluesy bends, funky comping, raw energy",
    }

    return universal_influences


# Chord progression complexity - uses Suno bracket tags
PROGRESSION_TYPES = {
    "None": "",
    "Complex Jazz": "[complex chord progression, jazz influences, extended harmonies]",
    "Dynamic Movement": "[dynamic chord progression, evolving structure]",
    "ii-V-I Changes": "[ii-V-I progression, bebop changes, guide tone movement]",
    "Giant Steps": "[complex progression, ascending minor thirds, giant steps harmony]",
    "Modal Vamp": "[modal vamp, pedal point, one-chord ostinato]",
    "Tritone Subs": "[tritone substitutions, chromatic bass, altered dominants]",
    "Quartal Voicings": "[quartal harmony, stacked fourths, open voicings]",
    "Blues Changes": "[jazz blues progression, I-IV-V turnaround, blue notes]",
    "Rich & Evolving": "[dynamic and complex chord progression, emotional depth]",
}

# Harmonic rhythm options
HARMONIC_RHYTHM = {
    "None": "",
    "Static Vamp": "[static harmony, drone bass, minimal chord movement]",
    "Slow Changes": "[slow harmonic rhythm, sustained chords, spacious]",
    "Medium Flow": "[medium harmonic rhythm, chord changes per bar]",
    "Fast Changes": "[fast harmonic rhythm, rapid chord movement, bebop feel]",
}

# Chord extension options
CHORD_EXTENSIONS = {
    "None": "",
    "7th Chords": "[seventh chords, maj7 min7 dom7 voicings]",
    "Extended 9ths/11ths": "[extended harmonies, 9th chords, 11th chords, rich voicings]",
    "Altered Tensions": "[altered dominants, sharp 9, flat 13, tension-rich harmony]",
    "Quartal/Sus": "[quartal voicings, sus4 sus2, open harmony]",
    "Sophisticated": "[sophisticated harmony, complex chords, jazz voicings]",
}

# Guitar stem replacement mode
GUITAR_REPLACE_REMOVE = ["fusion", "lead piano", "expressive soloist", "piano solo",
                         "keyboard solo", "piano melody", "piano lead"]
GUITAR_REPLACE_APPEND = ("guitar is always the primary melodic voice, "
                         "other instruments provide only harmonic and rhythmic support")

# =============================================================================
# UNIVERSAL (from workflow_builder)
# =============================================================================

# Major keys with emotional descriptions
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

# Minor keys with emotional descriptions
MINOR_KEYS = {
    "A Minor": "Sad, introspective, sincere (acoustic ballads, emo, lo-fi)",
    "E Minor": "Haunting, melancholic, mysterious (metal, alt rock, cinematic)",
    "D Minor": "Dramatic, tragic, emotional (classical, folk noir, film scoring)",
    "B Minor": "Dark, brooding, poetic (indie, alt-pop, gothic rock)",
    "F# Minor": "Tense, sorrowful, expressive (experimental, downbeat pop, EDM)",
    "C# Minor": "Ethereal, romantic, haunting (dream pop, ambient, solo piano)",
    "G Minor": "Bold, mournful, stormy (classical, jazz, moody pop)",
}

# Musical modes
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

# Modes grouped by key quality (for filtering)
MAJOR_MODES = ["Ionian (Major)", "Lydian", "Mixolydian"]
MINOR_MODES = ["Dorian", "Phrygian", "Aeolian (Minor)"]


def get_modes_for_key_quality(is_major: bool) -> list:
    """
    Get modes appropriate for major or minor key quality.

    Args:
        is_major: True for major keys, False for minor keys

    Returns:
        List of mode names appropriate for the key quality
    """
    if is_major:
        return MAJOR_MODES
    else:
        return MINOR_MODES


# Time signatures
TIME_SIGNATURES = {
    "4/4": "Standard, driving, marching (most common)",
    "3/4": "Waltz, flowing, romantic",
    "6/8": "Rolling, compound, shuffle feel",
    "2/4": "March, polka, rapid-fire",
    "12/8": "Swinging triplets, soulful, gospel groove",
    "5/4": "Odd, progressive, unsettling",
    "7/8": "Complex, prog rock, asymmetric",
}

# Tempo ranges
TEMPO_RANGES = {
    "None": "",
    "Slow (60-80 BPM)": "Intimate, meditative, slow-burning",
    "Mid-tempo (80-110 BPM)": "Groovy, versatile, laid-back groove",
    "Upbeat (110-130 BPM)": "Energetic, punchy and upbeat, driving rhythm",
    "Fast (130+ BPM)": "High energy, dance, urgency",
}

# Mood variations
MOOD_VARIATIONS = {
    "None": "",
    "Mellow": "mellow, relaxed atmosphere, smooth tone",
    "Intimate": "intimate, soft dynamics, delicate touch",
    "Uplifting": "uplifting, positive energy, bright melody",
    "Energetic": "energetic, driving intensity, aggressive attack",
    "Melancholic": "melancholic, emotional depth, weeping lines",
    "Dreamy": "dreamy, floating atmosphere, reverb-laden",
    "Dark": "dark, brooding atmosphere, minor phrases",
    "Searching": "searching, harmonic tension, exploratory lines",
}

# Song section types
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

# Poetic meters for lyrics
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

# Audio quality template
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

# Default section presets per genre
DEFAULT_SECTIONS = {
    "Pop": ["Intro", "Verse", "Pre-Chorus", "Chorus", "Verse", "Chorus", "Bridge", "Chorus", "Outro"],
    "Rock": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Solo", "Chorus", "Outro"],
    "EDM": ["Intro", "Buildup", "Drop", "Breakdown", "Buildup", "Drop", "Outro"],
    "Hip-Hop": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Verse", "Outro"],
    "Jazz": ["Intro", "Verse", "Solo", "Verse", "Solo", "Outro"],
    "Meditation": ["Intro", "Verse", "Verse", "Bridge", "Verse", "Outro"],
    "Ambient": ["Intro", "Verse", "Breakdown", "Verse", "Outro"],
    "default": ["Intro", "Verse", "Chorus", "Verse", "Chorus", "Bridge", "Chorus", "Outro"],
}

# =============================================================================
# SECTION INSTRUMENTS - Suggestions by genre, section type, and mood
# =============================================================================

SECTION_INSTRUMENTS = {
    "Jazz": {
        "Intro": {
            "Mellow": "soft brushed drums, walking bass intro, gentle piano",
            "Intimate": "rubato piano, light bass, sparse drums",
            "Energetic": "snappy drum fill, bright piano chord, punchy bass",
            "Dark": "sparse bass notes, moody piano, brush sticks",
            "Dreamy": "sustained piano chords, soft bass, ambient brushes",
            "default": "gentle piano intro, soft drums, walking bass"
        },
        "Verse": {
            "Mellow": "warm guitar melody, soft comping piano, walking bass",
            "Intimate": "delicate guitar, sparse piano, gentle bass",
            "Energetic": "punchy rhythm section, walking bass, crisp drums",
            "Dark": "minor guitar phrases, dark piano voicings, deep bass",
            "Dreamy": "floating guitar lines, Rhodes piano, soft bass",
            "default": "guitar lead, piano comping, walking bass"
        },
        "Chorus": {
            "Mellow": "full quartet, slightly building, warm tone",
            "Energetic": "driving rhythm, full energy, walking bass",
            "Dark": "intense minor harmonies, powerful bass, driving drums",
            "default": "full band, building intensity"
        },
        "Solo": {
            "Mellow": "expressive guitar solo, sparse piano accompaniment",
            "Energetic": "virtuosic guitar runs, driving rhythm section",
            "Dark": "angular guitar lines, moody backing",
            "default": "guitar solo, sparse accompaniment"
        },
        "Bridge": {
            "default": "harmonic exploration, rubato section, building tension"
        },
        "Outro": {
            "Mellow": "fading piano, soft drums, gentle close",
            "Energetic": "driving finish, powerful final chord",
            "default": "gentle fade, final chord, soft drums"
        },
    },
    "Rock": {
        "Intro": {
            "Mellow": "clean guitar arpeggios, soft drums",
            "Energetic": "power chord blast, driving drums, aggressive",
            "Dark": "distorted guitar riff, heavy drums, ominous bass",
            "default": "guitar riff, solid drums, punchy bass"
        },
        "Verse": {
            "Mellow": "clean guitar chords, steady rhythm, soft dynamics",
            "Energetic": "driving guitar, pounding drums, pumping bass",
            "Dark": "heavy riff, dark tone, aggressive bass",
            "default": "rhythm guitar, solid drums, bass groove"
        },
        "Pre-Chorus": {
            "default": "building intensity, rising guitars, drum fills"
        },
        "Chorus": {
            "Mellow": "full band, melodic guitars, anthemic feel",
            "Energetic": "explosive energy, power chords, crashing cymbals",
            "Dark": "heavy wall of sound, aggressive guitars",
            "default": "full band explosion, big guitars, driving drums"
        },
        "Solo": {
            "Mellow": "melodic guitar solo, emotional bends",
            "Energetic": "shredding guitar solo, fast runs, wah pedal",
            "Dark": "dark solo, minor pentatonic, aggressive tone",
            "default": "guitar solo, expressive lead, backing power chords"
        },
        "Bridge": {
            "default": "stripped back section, building tension, quiet to loud"
        },
        "Breakdown": {
            "default": "half-time drums, heavy riffs, massive sound"
        },
        "Outro": {
            "default": "fading guitars, final chord, drum fill finish"
        },
    },
    "Pop": {
        "Intro": {
            "Mellow": "soft synth pad, light drums, gentle melody",
            "Uplifting": "bright piano, upbeat drums, positive vibe",
            "Energetic": "punchy synths, four-on-floor, catchy hook",
            "default": "catchy hook, light production, clean sound"
        },
        "Verse": {
            "Mellow": "acoustic guitar, soft beat, intimate vocals",
            "Uplifting": "bright production, bouncy bass, positive energy",
            "Energetic": "driving beat, synth stabs, energetic bass",
            "default": "clean production, steady rhythm, melodic hooks"
        },
        "Pre-Chorus": {
            "default": "building energy, rising synths, drum builds"
        },
        "Chorus": {
            "Mellow": "full but soft, layered vocals, warm",
            "Uplifting": "explosive joy, big hooks, soaring melody",
            "Energetic": "massive drop, full production, anthemic",
            "default": "big hooks, full production, catchy melody"
        },
        "Bridge": {
            "default": "stripped back, emotional moment, building return"
        },
        "Post-Chorus": {
            "default": "infectious hook, dance break, memorable riff"
        },
        "Outro": {
            "default": "fading chorus, final hook, gentle close"
        },
    },
    "EDM": {
        "Intro": {
            "Energetic": "atmospheric synths, rising energy, anticipation",
            "Dark": "dark pads, ominous bass, tension building",
            "default": "atmospheric pads, subtle beat, building mood"
        },
        "Buildup": {
            "Energetic": "rising synths, snare rolls, intense build",
            "Dark": "dark risers, aggressive buildup, tension",
            "default": "rising filter sweep, snare build, increasing energy"
        },
        "Drop": {
            "Energetic": "massive bass drop, punchy kicks, full energy",
            "Dark": "heavy bass, aggressive synths, dark drops",
            "default": "massive bass drop, punchy synths, full release"
        },
        "Breakdown": {
            "Mellow": "stripped back, melodic moment, soft pads",
            "default": "melodic section, soft pads, emotional moment"
        },
        "Outro": {
            "default": "fading energy, final drop reference, outro pads"
        },
    },
    "Hip-Hop": {
        "Intro": {
            "Mellow": "lo-fi beat, soft sample, laid back",
            "Energetic": "hard-hitting intro, trap drums, 808 bass",
            "Dark": "dark sample, ominous beat, heavy bass",
            "default": "beat intro, sample chop, setting the vibe"
        },
        "Verse": {
            "Mellow": "smooth beat, jazzy samples, laid back flow",
            "Energetic": "hard drums, aggressive 808, trap hi-hats",
            "Dark": "dark production, heavy bass, intense beat",
            "default": "driving beat, punchy drums, bass-heavy"
        },
        "Chorus": {
            "Mellow": "melodic hook, smooth production, catchy",
            "Energetic": "anthemic hook, full production, memorable",
            "default": "catchy hook, full beat, memorable melody"
        },
        "Outro": {
            "default": "beat continues, fading out, final ad-libs"
        },
    },
    "Ambient": {
        "Intro": {
            "default": "evolving pad, subtle texture, atmospheric"
        },
        "Verse": {
            "default": "floating textures, sparse melody, spacious"
        },
        "Buildup": {
            "default": "layering synths, rising tension, evolving"
        },
        "Drop": {
            "default": "full sonic wash, deep bass, immersive"
        },
        "Breakdown": {
            "default": "stripped textures, breathing room, minimal"
        },
        "Outro": {
            "default": "fading textures, dissolving into silence"
        },
    },
    "Meditation": {
        "Intro": {
            "Mellow": "gentle singing bowls, soft breath, nature sounds",
            "Dreamy": "ethereal pads, distant wind chimes, soft drone",
            "default": "soft pad, gentle bells, calming atmosphere"
        },
        "Verse": {
            "Mellow": "warm drone, soft flute, gentle water sounds",
            "Dreamy": "floating tones, celestial harmonics, soft harp",
            "default": "sustained pad, gentle melody, breathing space"
        },
        "Chorus": {
            "default": "layered harmonics, warm resonance, peaceful expansion"
        },
        "Bridge": {
            "default": "deeper tones, grounding frequencies, still moment"
        },
        "Breakdown": {
            "default": "minimal texture, pure silence, single tone"
        },
        "Outro": {
            "Mellow": "fading bowls, returning to silence, final breath",
            "default": "gentle fade, dissolving tones, peaceful silence"
        },
    },
    "Electronic": {
        "Intro": {
            "default": "synth arpeggio, electronic pulse, building"
        },
        "Verse": {
            "default": "driving synths, electronic beat, pulsing bass"
        },
        "Buildup": {
            "default": "rising arpeggios, filter sweep, snare build"
        },
        "Drop": {
            "default": "full synth drop, massive bass, energetic"
        },
        "Breakdown": {
            "default": "melodic interlude, softer synths, breathing"
        },
        "Outro": {
            "default": "fading arpeggios, closing synth pad"
        },
    },
    "Metal": {
        "Intro": {
            "default": "heavy riff, double bass drums, aggressive"
        },
        "Verse": {
            "default": "palm-muted riffs, driving drums, heavy bass"
        },
        "Chorus": {
            "default": "massive wall of sound, powerful vocals section"
        },
        "Solo": {
            "default": "shredding guitar solo, aggressive tone, fast runs"
        },
        "Breakdown": {
            "default": "heavy breakdown, half-time drums, crushing riffs"
        },
        "Outro": {
            "default": "final riff, powerful ending, crash cymbal"
        },
    },
    "Lo-fi": {
        "Intro": {
            "default": "vinyl crackle, soft piano, mellow beat"
        },
        "Verse": {
            "default": "dusty drums, jazzy chords, warm bass"
        },
        "Chorus": {
            "default": "melodic hook, soft keys, tape saturation"
        },
        "Outro": {
            "default": "fading beat, vinyl noise, gentle close"
        },
    },
    "default": {
        "Intro": {"default": "atmospheric intro, setting the mood"},
        "Verse": {"default": "main progression, moderate energy"},
        "Pre-Chorus": {"default": "building tension, rising energy"},
        "Chorus": {"default": "full energy, main hook, memorable"},
        "Bridge": {"default": "contrast section, new perspective"},
        "Solo": {"default": "instrumental feature, expressive"},
        "Breakdown": {"default": "stripped back, building tension"},
        "Buildup": {"default": "rising energy, anticipation"},
        "Drop": {"default": "full release, maximum energy"},
        "Outro": {"default": "closing section, resolving"},
    },
}


def get_section_instruments(genre: str, section_type: str, mood: str = "default") -> str:
    """
    Get suggested instruments for a section based on genre and mood.

    Args:
        genre: The music genre
        section_type: The section type (Intro, Verse, Chorus, etc.)
        mood: The mood (Mellow, Energetic, Dark, etc.) or "default"

    Returns:
        String with instrument/mood suggestions for the section
    """
    # Get genre mapping, fall back to default
    genre_map = SECTION_INSTRUMENTS.get(genre, SECTION_INSTRUMENTS.get("default", {}))

    # Get section mapping
    section_map = genre_map.get(section_type, {})
    if not section_map:
        # Try default genre if specific genre doesn't have this section
        section_map = SECTION_INSTRUMENTS.get("default", {}).get(section_type, {})

    # Get mood-specific or default
    return section_map.get(mood, section_map.get("default", ""))

# =============================================================================
# LYRIC TEMPLATES (from prompt_generator)
# =============================================================================

LYRIC_TEMPLATES = {
    "None": "",
    "Anti-Listening (Controlled)": (
        "[Opening Field]\n"
        "(intervallic harmonic block, no tonal center)\n"
        "(chromatic vertical cluster, avoid triadic harmony)\n"
        "(non-functional harmony, no root motion)\n"
        "\n"
        "[Primary Material]\n"
        "(fragmented thematic cell, harmonic displacement)\n"
        "(asymmetric phrase length, tonal center displaced)\n"
        "(fragmented thematic cell, chromatic instability)\n"
        "\n"
        "[Transition]\n"
        "(abrupt harmonic interruption)\n"
        "(abrupt harmonic interruption)\n"
        "\n"
        "[Thematic Field]\n"
        "(intervallic harmonic block, avoid triadic harmony)\n"
        "(non-parallel harmonic shift, no functional root motion)\n"
        "(chromatic vertical cluster, unstable harmonic field)\n"
        "\n"
        "[Instrumental Break]\n"
        "(lead guitar solo, angular phrasing, harmony remains unstable)\n"
        "(lead guitar solo, sparse gestures, vertical harmony emphasis)\n"
        "\n"
        "[Final Field]\n"
        "(harmonic field transforms, still no tonal center)\n"
        "(chromatic suspension, no cadence)\n"
        "\n"
        "[Outro]\n"
        "(harmonic suspension, unresolved ending)"
    ),
    "Anti-Tonal (Hard)": (
        "[Opening Field]\n"
        "(intervallic material, no tonal grounding)\n"
        "(chromatic displacement, avoid triadic harmony)\n"
        "(non-functional vertical harmony)\n"
        "\n"
        "[Material Field A]\n"
        "(fragmented thematic cell, rotating tonal center)\n"
        "(intervallic displacement, asymmetric phrasing)\n"
        "(fragmented thematic cell, no resolution)\n"
        "\n"
        "[Interruption]\n"
        "(abrupt harmonic cut)\n"
        "(abrupt harmonic cut)\n"
        "\n"
        "[Material Field B]\n"
        "(chromatic vertical cluster, no functional root motion)\n"
        "(non-parallel harmonic shift, tonal center displaced)\n"
        "(intervallic tension, unstable harmonic field)\n"
        "\n"
        "[Development Field]\n"
        "(thematic fragments recombined, increased instability)\n"
        "(chromatic expansion, no repetition)\n"
        "(intervallic tension, no tonal center)\n"
        "\n"
        "[Instrumental Break]\n"
        "(lead guitar solo, angular phrasing, harmony remains unstable)\n"
        "(lead guitar solo, physically playable but uncomfortable)\n"
        "(lead guitar solo, rests used as tension)\n"
        "\n"
        "[Post-Solo Field]\n"
        "(clean guitar texture returns, non-functional harmony)\n"
        "(intervallic displacement continues)\n"
        "\n"
        "[Outro]\n"
        "(open harmonic field, unresolved)"
    ),
    "Radical / Anti-Musical": (
        "[Disorientation]\n"
        "(intervallic harmonic block, no tonal center)\n"
        "(chromatic vertical cluster, avoid triadic harmony)\n"
        "(non-functional harmony, no root motion)\n"
        "\n"
        "[Fragment Field]\n"
        "(fragmented cell, harmonic displacement)\n"
        "(fragmented cell, chromatic instability)\n"
        "(fragmented cell, asymmetric phrase length)\n"
        "\n"
        "[Void]\n"
        "(silence or sustained texture, harmonic suspension)\n"
        "(silence or sustained texture, harmonic suspension)\n"
        "\n"
        "[Instability Field]\n"
        "(non-parallel harmonic blocks, no progression)\n"
        "(intervallic collision, tonal center erased)\n"
        "(chromatic vertical mass, no functional grounding)\n"
        "\n"
        "[Instrumental Break]\n"
        "(lead guitar solo, sparse angular gestures)\n"
        "(lead guitar solo, physical but intentionally awkward)\n"
        "(lead guitar solo, harmony resists normalization)\n"
        "\n"
        "[Collapse Field]\n"
        "(clean guitar texture, harmonic field deteriorates)\n"
        "(intervallic residue, no closure)\n"
        "\n"
        "[Outro]\n"
        "(abrupt or unresolved ending)"
    ),
    "Pulse Field": (
        "[Opening]\n"
        "(pulse established, no tonal center)\n"
        "\n"
        "[Pulse Field]\n"
        "(persistent pulse, non-functional harmony)\n"
        "(persistent pulse, intervallic displacement)\n"
        "(persistent pulse, avoid triadic harmony)\n"
        "\n"
        "[Thematic Friction]\n"
        "(fragmented material, pulse maintained)\n"
        "(harmonic tension increases, pulse unchanged)\n"
        "\n"
        "[Pulse Field]\n"
        "(pulse continues, tonal center rotates)\n"
        "(pulse altered, harmonic instability)\n"
        "\n"
        "[Instrumental Break]\n"
        "(lead guitar solo, phrasing pushes against pulse)\n"
        "(lead guitar solo, angular lines, no resolution)\n"
        "(lead guitar solo, harmony resists normalization)\n"
        "\n"
        "[Final Pulse]\n"
        "(pulse weakens, harmonic field unstable)\n"
        "(pulse fragments)\n"
        "\n"
        "[Outro]\n"
        "(pulse stops abruptly, unresolved)"
    ),
}
