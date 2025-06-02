from fastapi import UploadFile
from core.config import Settings
import os
import re
import time
from typing import Tuple

class FileService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        allowed_types = self.settings.FILE_ALLOWED_TYPES
        max_size = self.settings.FILE_MAX_SIZE

        if file.content_type not in allowed_types:
            return False, 'Invalid file type, ' + file.content_type

        if file.size > max_size:
            return False, 'File size exceeds the limit of ' + str(max_size) + ' bytes'

        return True, 'valid file'

    def get_sanitized_filename(self, original_filename: str) -> str:
        # Clean the file name to avoid issues with special characters and spaces
        filename = original_filename.replace(" ", "_")
        filename = re.sub(r'[^\w.]', '', filename.strip())
        
        # Add current timestamp to the file name
        timestamp = int(round(time.time() * 1000))
        return f"{timestamp}_{filename}"

    def get_project_path(self, base_path: str, project_id: str) -> str:
        project_path = os.path.join(base_path, project_id)
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        return project_path

    def get_file_path(self, project_path: str, filename: str) -> str:
        return os.path.join(project_path, filename)
