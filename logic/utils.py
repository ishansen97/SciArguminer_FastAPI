import re

from typer.models import ArgumentInfo

from models.Argument import Argument
from models.Relation import Relation


def extract_text(text, max_length=512):
    """
    Extract up to `max_length` characters from the given text,
    ensuring the last character is part of a complete word.

    Args:
        text (str): The input text.
        max_length (int): The maximum number of characters to extract.

    Returns:
        str: The extracted text.
    """
    # Truncate the text to the maximum length
    truncated = " ".join(text.split()[:max_length])

    # Ensure the truncated text ends with a complete word
    if len(truncated) == max_length and not truncated[-1].isspace():
        while truncated and not truncated[-1].isspace():
            truncated = truncated[:-1]

    return truncated.strip()

def extract_components(text):
    # Regex pattern to capture text within square brackets
    # pattern = r'\[([^]]+?\s\|\s\w+)(?:\s*\|.*)?\]'
    pattern = r'\[([^]]+?\s\|\s\w+)'

    matches = re.findall(pattern, text)

    # Print extracted argument components
    # for idx, match in enumerate(matches):
    # print(f'{idx+1}) {match}')
    split_components = [match.split('|') for match in matches]
    # print(split_components)
    # components = [match.split('|')[0].strip() for match in matches]
    return split_components

def extract_argument_info(text, content):
    argument, argType = text[0].strip(), text[1]
    index = content.find(argument)
    start, end = -1, -1
    if index > -1:
        start, end = index, index + len(argument)

    return Argument(argument, start, end, argType)


def extract_relations(text):
    rel_pattern = r'\[\s*([^|\]=]+)\s*\|\s*([^|\]=]+)\s*\|\s*([^=|\]]+)\s*=\s*([^\]]+)\s*\]'
    matches = re.finditer(rel_pattern, text)

    results: list[Relation] = []

    for match in matches:
        head = Argument(match.group(1).strip(), 0, 0, match.group(2))
        tail = Argument(match.group(4).strip(), 0, 0, '')
        relation = match.group(3).strip()
        results.append(Relation(head, tail, relation))

    return results