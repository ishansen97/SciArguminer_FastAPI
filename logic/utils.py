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
from logic.constants import REL_TYPES, ARG_TYPES
from models.Argument import Argument
from models.Relation import Relation
from models.Report import ReportModel
from models.Response import ReportResponseModel
from models.Summary import Summary

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

def extract_argument_info(text, content):
    argument, argType = text[0].strip(), text[1]
    # consider only the first 5 words for text search (temporary solution)
    search_text = ' '.join(argument.split(' ')[:5]) if len(argument.split(' ')) > 5 else argument
    # index = content.find(argument)
    index = content.find(search_text)
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
    invalid_headings = ['', 'acknowledgments']
    return True if heading.lower() not in invalid_headings else False

def should_end_processing(heading: str) -> bool:
    ending_headings = ['', 'acknowledgments']
    return True if heading.lower() in ending_headings else False

