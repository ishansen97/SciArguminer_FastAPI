import os
from pathlib import Path
from typing import List

from fastapi import UploadFile
from science_parse_api.api import parse_pdf

from config import ConfigManager
from models.Section import Section

config = ConfigManager().config

def save_upload_file(upload_file: UploadFile):
    """
    Saves the uploaded file to the 'temp_files' directory.

    Args:
        upload_file (UploadFile): The uploaded file to save.

    Returns:
        str: The path where the file was saved.
    """
    temp_dir = config.upload_dir
    os.makedirs(temp_dir, exist_ok=True)  # Ensure directory exists

    save_path = os.path.join(temp_dir, upload_file.filename)
    with upload_file.file as src:
        with open(save_path, "wb") as dst:
            while chunk := src.read(1024):  # Read in chunks
                dst.write(chunk)

    return save_path

def process_pdf_file(file_path) -> List[Section]:
    host = config.science_parse_api_host
    port = config.science_parse_api_port

    information = []
    path = Path(file_path)
    output_dict = parse_pdf(host, path, port=port)
    output_sections = output_dict['sections'][:5]

    for idx, section in enumerate(output_sections):
        key = 'heading'
        title = ''
        if key in section:
            title = section[key]
        elif idx == 0:
            title = 'Abstract'
        text = section['text']
        sect_obj = Section(title, text)
        information.append(sect_obj)

    return information