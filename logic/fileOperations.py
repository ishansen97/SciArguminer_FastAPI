import os
from pathlib import Path
import logging
import torch

from fastapi import UploadFile
from science_parse_api.api import parse_pdf

from config import ConfigManager
from models.Section import Section

config = ConfigManager().config
logger = logging.getLogger(__name__)

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

def process_pdf_file(file_path):
    host = config.science_parse_api_host
    port = config.science_parse_api_port

    information = []
    arguments = []
    relations = []
    path = Path(file_path)
    output_dict = parse_pdf(host, path, port=port)
    output_sections = output_dict['sections']

    logger.debug(f'model type: {config.model_type}')
    logger.debug(f"device type: {'gpu' if torch.cuda.is_available() else 'cpu' }")

    for idx, section in enumerate(output_sections):
        key = 'heading'
        title = ''
        if key in section:
            title = section[key]
        elif idx == 0:
            title = 'Abstract'
        text = section['text']
        sect_obj = Section(title, text)

        logger.info(f'Staring to processing the section {title}')

        sect_obj.populate_inferenced_text()
        information.append(sect_obj)
        arguments.extend(sect_obj.arguments)
        relations.extend(sect_obj.relations)

        logger.info(f'Finished processing the section {title}')

    os.remove(file_path)
    logger.info(f'File {file_path} has been deleted')
    return information, arguments, relations