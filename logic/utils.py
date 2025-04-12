import os
import re
import logging
import json
from datetime import datetime
from itertools import groupby
from pathlib import Path

from fastapi.templating import Jinja2Templates
from weasyprint import HTML

from db.models import Report
from logic import modelOperations
from logic.constants import REL_TYPES, ARG_TYPES
from models.Argument import Argument
from models.Relation import Relation
from models.Report import ReportModel
from models.Response import ReportResponseModel
from models.Summary import Summary
from models.ZoneLabels import ZoneLabel
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
# Get absolute path to templates/ from current file
BASE_DIR = Path(__file__).resolve().parent.parent  # goes from logic/ to project root
TEMPLATES_DIR = BASE_DIR / "templates"
IMAGES_DIR = BASE_DIR / "images"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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


def extract_components_with_zones(text):
    pattern = r'(\(\(\s+\w+\s+\)\))\[([^]]+?\s\|\s\w+)'
    matches = re.findall(pattern, text)
    components = []

    for match in matches:
        components.append({
            'zone': remove_zoning_paranthesis(match[0]),
            'argument_comps': [split_part.strip() for split_part in match[1].split('|')]
        })

    return components

def extract_argument_info(text, content, title):
    argument, argType = text[0].strip(), text[1]
    # consider only the first 5 words for text search (temporary solution)
    search_text = ' '.join(argument.split(' ')[:5]) if len(argument.split(' ')) > 5 else argument
    # index = content.find(argument)
    index = content.find(search_text)
    start, end = -1, -1
    if index > -1:
        start, end = index, index + len(argument)

    return Argument(argument, start, end, argType, title, '')

def extract_argument_info_with_zoning(arg_info, content, title):
    zone, argument, argType = arg_info['zone'], arg_info['argument_comps'][0], arg_info['argument_comps'][0]
    # consider only the first 5 words for text search (temporary solution)
    search_text = ' '.join(argument.split(' ')[:5]) if len(argument.split(' ')) > 5 else argument
    # index = content.find(argument)
    index = content.find(search_text)
    start, end = -1, -1
    if index > -1:
        start, end = index, index + len(argument)

    return Argument(argument, start, end, argType, title, zone)


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


def extract_relations_with_zones(text):
    rel_pattern = r'(\(\(\s+\w+\s+\)\))\[\s*([^|\]=]+)\s*\|\s*([^|\]=]+)\s*\|\s*([^=|\]]+)\s*=\s*([^\]]+)\s*\]'
    tail_pattern = r'(\(\(\s+\w+\s+\)\))\[\s*([^|\]=]+)\s*\|\s*([^|\]=]+)\s*\]'
    # matches = re.search(rel_pattern, text)
    matches = re.finditer(rel_pattern, text)
    tail_matches = re.finditer(tail_pattern, text)

    results = []
    tail_results = []
    for match in matches:
        result = {}
        result['head_zone'] = match.group(1)
        result['head'] = match.group(2)
        result['head_comp'] = match.group(3)
        result['rel_type'] = match.group(4)
        result['tail'] = match.group(5)
        results.append(result)

    for match in tail_matches:
        result = {}
        result['tail_zone'] = match.group(1)
        result['tail'] = match.group(2)
        result['tail_comp'] = match.group(3)
        tail_results.append(result)

    return results, tail_results

def remove_zoning_paranthesis(zone_text):
    return zone_text.replace("((", "").replace("))", "").strip()


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

def get_report_models(report: Report) -> ReportResponseModel:
    model = ReportResponseModel()
    model.id = report.id
    model.name = report.paper
    model.date = datetime.strftime(report.created, "%Y-%m-%d")

    return model

def get_report_content(report: ReportModel) -> bytes:
    logo_path = Path(os.path.join(IMAGES_DIR, 'Sci-Arguminer_Logo.jpg')).resolve()
    logo_url = logo_path.as_uri()  # 'file://C:/...' on Windows, 'file:///home/...' on Linux

    html_content = templates.get_template('newReportTemplate.html').render({
        'logo_path': logo_url,
        'reportName': report.reportName,
        'authorNames': report.authorNames,
        'arguments': report.arguments,
        'relations': report.relations,
        'summary': report.summary,
    })
    pdf_file = HTML(string=html_content).write_pdf()
    return pdf_file
# def get_report_content(summary: dict[str, dict[str, int]]) -> bytes:
#     html_content = templates.get_template('reportTemplate.html').render({
#         'summary': summary,
#     })
#     pdf_file = HTML(string=html_content).write_pdf()
#     return pdf_file
#
def is_valid_section_heading(heading: str) -> bool:
    invalid_headings = ['']
    return True if heading.lower() not in invalid_headings else False

def should_end_processing(heading: str) -> bool:
    ending_headings = ['acknowledgments']
    return True if heading.lower() in ending_headings else False

def process_global_local_arguments(globalZones: list[ZoneLabel], arguments: list[Argument]):
    base_sentence_similarities = {}
    threshold = 0.3
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    for zoneIdx, zoningLabel in enumerate(globalZones):
        base_sentence_similarities[zoneIdx + 1] = {}
        for argument in arguments:
            similarity_score = modelOperations.get_sentence_embeddings(sentence_model, zoningLabel.sentence, argument.text).item()
            if similarity_score > threshold:
                base_sentence_similarities[zoneIdx+1] = {argument: argument, 'similarity': "{score:.4f}".format(score=similarity_score)}

    return base_sentence_similarities



