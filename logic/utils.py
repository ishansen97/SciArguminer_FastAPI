import re
import logging
from datetime import datetime
from itertools import groupby

from logic.constants import REL_TYPES, ARG_TYPES
from models.Argument import Argument
from models.Relation import Relation
from models.Summary import Summary

logger = logging.getLogger(__name__)

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
    pattern = r'\[([^]]+?\s\|\s\w+)'

    matches = re.findall(pattern, text)
    split_components = [match.split('|') for match in matches]
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

def get_datetime(text):
    if text is not None:
        # return datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
        return datetime.strptime(text, '%Y-%m-%d')
    return None

def get_summary(arguments: list[Argument], relations: list[Relation]) -> Summary:
    relations_sorted = sorted(relations, key=lambda r: r.relation.strip())
    arguments_sorted = sorted(arguments, key=lambda a: a.type.strip())

    relation_groups = groupby(relations_sorted, key=lambda r: r.relation.strip())
    argument_groups = groupby(arguments_sorted, key=lambda r: r.type.strip())

    relation_group_list = [(key, list(group)) for key, group in relation_groups if key in REL_TYPES]
    argument_group_list = [(key, list(group)) for key, group in argument_groups if key in ARG_TYPES]

    relation_groups_total = sum(list(map(lambda pair: len(pair[1]), relation_group_list)), 0)
    argument_groups_total = sum(list(map(lambda pair: len(pair[1]), argument_group_list)), 0)

    relation_summary = {key: len(group) for key, group in relation_group_list if key in REL_TYPES}
    argument_summary = {key: len(group) for key, group in argument_group_list if key in ARG_TYPES}

    relation_summary = {**relation_summary, 'totalCount': relation_groups_total}
    argument_summary = {**argument_summary, 'totalCount': argument_groups_total}

    summary = Summary(argument_summary, relation_summary)
    return summary