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

def answer(arr):
    if type(arr) == type(''):
        _arr = ANSWERS[arr]
    else:
        _arr = arr
    return _arr[random.randint(0, len(_arr) - 1)]