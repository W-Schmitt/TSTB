import random

ANSWERS = {
    "ENABLE": [
        "Let's do this!"
    ],
    "DISABLE": [
        "Alright, bye!"
    ],
    "TOP_SUFFIX": [
        ' scored!'
    ]
}

def answer(string):
    return ANSWERS[string][random.randint(0, len(ANSWERS[string]) - 1)]