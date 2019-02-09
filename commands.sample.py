import re

RE_SPECIAL = {
    "RE_START": "( |^|\.|\')+",
    "RE_END": "( |$|\.|\')+"
}

RE_TEMPLATES = {
    "TOPSCORE": "YOUR-SCORING-REGEX",
    "TOP": "YOUR-LEADERBOARD-COMMAND",
    # INSERT YOUR COMMANDS HERE
    "ENABLE": "YOUR-ENABLE-COMMAND",
    "DISABLE": "YOUR-DISABLE-COMMAND"
}

RE = {}

for key, tmpl in RE_TEMPLATES.items():
    RE[key] = re.compile(RE_SPECIAL["RE_START"] + tmpl + RE_SPECIAL["RE_END"], re.IGNORECASE)