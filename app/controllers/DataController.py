from .BaseController import BaseController
from services.file.FileService import FileService
from fastapi import UploadFile


class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.file_service = FileService(settings=self.app_settings)
        
    def validate_file(self, file: UploadFile):
        return self.file_service.validate_file(file)

    def get_file_path(self, project_id: str, file_name: str):
        project_path = self.file_service.get_project_path(project_id)
        sanitized_filename = self.file_service.get_sanitized_filename(file_name)
        file_path = self.file_service.get_file_path(project_path, sanitized_filename)
        return file_path, sanitized_filename
