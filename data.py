# Multiple style presets for radical variety
# STRICTLY quartet only: guitar (lead), piano (comping), bass, drums
# Guitar is the primary melodic/lead instrument, piano provides harmonic support
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
}

# Keep original for backwards compatibility
BASE_PROMPT = STYLE_PRESETS["Smooth Jazz"]

# Key signatures with modal implications
KEY_SIGNATURES = {
    "None": "",
    "C major": "in C major, bright Ionian clarity",
    "G major": "in G major, open pastoral Ionian",
    "D major": "in D major, bright and warm",
    "A major": "in A major, brilliant and uplifting",
    "E major": "in E major, bright and resonant",
    "F major": "in F major, warm Lydian-tinged",
    "Bb major": "in Bb major, warm jazz standard key",
    "Eb major": "in Eb major, classic jazz key, rich",
    "Ab major": "in Ab major, lush and romantic",
    "Db major": "in Db major, dreamy Lydian colors",
    "D Dorian": "in D Dorian mode, minor with raised 6th, jazz minor feel",
    "A Dorian": "in A Dorian mode, cool minor jazz color",
    "E Phrygian": "in E Phrygian mode, Spanish-tinged, dark exotic",
    "F Lydian": "in F Lydian mode, bright raised 4th, dreamy",
    "G Mixolydian": "in G Mixolydian mode, dominant feel, bluesy",
    "A minor": "in A minor, Aeolian melancholy",
    "D minor": "in D minor, dark and passionate",
    "E minor": "in E minor, somber and reflective",
    "G minor": "in G minor, dramatic and emotional",
    "C minor": "in C minor, intense and stormy",
}

# Style influences - guitar as lead focus
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

TEMPO_VARIATIONS = {
    "None": "",
    "Slow (60-80 BPM)": "slow tempo, around 70 BPM, space for guitar expression",
    "Medium (80-110 BPM)": "medium tempo, around 95 BPM, relaxed swing feel",
    "Uptempo (110-130 BPM)": "uptempo, around 120 BPM, driving energy",
    "Fast (130+ BPM)": "fast tempo, energetic pace, virtuosic guitar",
}

MOOD_VARIATIONS = {
    "None": "",
    "Mellow": "mellow, relaxed atmosphere, smooth guitar tone",
    "Intimate": "intimate, soft dynamics, delicate guitar touch",
    "Uplifting": "uplifting, positive energy, bright guitar melody",
    "Energetic": "energetic, driving intensity, aggressive guitar attack",
    "Melancholic": "melancholic, emotional depth, weeping guitar lines",
    "Dreamy": "dreamy, floating atmosphere, reverb-laden guitar",
    "Dark": "dark, brooding atmosphere, minor guitar phrases",
    "Searching": "searching, harmonic tension, exploratory guitar lines",
}

INTRO_VARIATIONS = {
    "None": "",
    "Guitar intro": "solo guitar intro, unaccompanied melody, band enters gradually",
    "Guitar chords intro": "guitar chord intro with arpeggios, rhythm section joins",
    "Ambient/Sparse": "atmospheric sparse intro, guitar harmonics, building arrangement",
    "Bass and guitar": "bass and guitar duo intro, piano and drums enter later",
    "Rubato guitar": "rubato guitar intro, free tempo, expressive bends",
    "Full band": "full quartet from the start, guitar states theme immediately",
}

# Chord progression complexity - uses Suno bracket tags for better recognition
# These avoid boring IVm7-Im7 patterns
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

# How often chords change
HARMONIC_RHYTHM = {
    "None": "",
    "Static Vamp": "[static harmony, drone bass, minimal chord movement]",
    "Slow Changes": "[slow harmonic rhythm, sustained chords, spacious]",
    "Medium Flow": "[medium harmonic rhythm, chord changes per bar]",
    "Fast Changes": "[fast harmonic rhythm, rapid chord movement, bebop feel]",
}

# Chord voicing complexity
CHORD_EXTENSIONS = {
    "None": "",
    "7th Chords": "[seventh chords, maj7 min7 dom7 voicings]",
    "Extended 9ths/11ths": "[extended harmonies, 9th chords, 11th chords, rich voicings]",
    "Altered Tensions": "[altered dominants, sharp 9, flat 13, tension-rich harmony]",
    "Quartal/Sus": "[quartal voicings, sus4 sus2, open harmony]",
    "Sophisticated": "[sophisticated harmony, complex chords, jazz voicings]",
}
