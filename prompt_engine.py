from data import BASE_PROMPT

def build_prompt(tonality="", mode_family="", guitar="", groove="",
                 tempo="", mood="", era="", intro=""):
    additions = [tonality, mode_family, guitar, groove, tempo, mood, era, intro]
    additions = [a for a in additions if a]
    return BASE_PROMPT + (", " + ", ".join(additions) if additions else "")