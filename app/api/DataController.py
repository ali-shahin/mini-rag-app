from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
import os
import re
import time


class DataController (BaseController):
    def __init__(self):
        super().__init__()

    def validate_file(self, file: UploadFile):
        allowed_types = self.app_settings.FILE_ALLOWED_TYPES
        max_size = self.app_settings.FILE_MAX_SIZE

        if file.content_type not in allowed_types:
            return False, 'Invalid file type, ' + file.content_type

        if file.size > max_size:
            return False, 'File size exceeds the limit of ' + str(max_size) + ' bytes'

        return True, 'valid file'

    def get_file_path(self, project_id: str, file_name: str):
        project_path = ProjectController().get_project_path(project_id)

        # clean the file name to avoid issues with special characters and spaces.
        file_name = file_name.replace(" ", "_")
        file_name = re.sub(r'[^\w.]', '', file_name.strip())

        # add current timestamp to the file name
        timestamp = int(round(time.time() * 1000))
        file_name = f"{timestamp}_{file_name}"

        file_path = os.path.join(project_path, file_name)
        return file_path, file_name
