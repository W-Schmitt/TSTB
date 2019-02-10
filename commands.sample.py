import re
import random
from answers import answer

RE_SPECIAL = {
    "RE_START": "( |^|\.|\')+",
    "RE_END": "( |$|\.|\')+"
}

COMMAND_TEMPLATES = {
    "TOPSCORE": {
        "RE": "YOUR-scoring-COMMAND-REGEX",
        "FUNCTION": answer
    },
    "TOP": {
        "RE": "YOUR-LEADERBOARD-COMMAND-REGEX",
        "FUNCTION": answer
    },
    # INSERT YOUR COMMANDS HERE
    "ENABLE": {
        "RE": "YOUR-ENABLE-COMMAND-REGEX",
        "FUNCTION": answer
    },
    "DISABLE": {
        "RE": "YOUR-DISABLE-COMMAND-REGEX",
        "FUNCTION": answer
    },
}

COMMANDS = {}

for key, cmd in COMMAND_TEMPLATES.items():
    COMMANDS[key] = {
        "RE": re.compile(RE_SPECIAL["RE_START"] + cmd['RE'] + RE_SPECIAL["RE_END"], re.IGNORECASE),
        "FUNCTION": cmd['FUNCTION']
    }