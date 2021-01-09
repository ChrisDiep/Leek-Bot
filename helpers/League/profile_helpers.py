import re


def clean_input(words):
    """ Removes non-alphanumeric values and joins the input together """
    parsed = ''.join(map(lambda word: re.sub(r'[^a-zA-Z0-9]', '', word), words))
    return parsed
