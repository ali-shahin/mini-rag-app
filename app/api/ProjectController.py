from .BaseController import BaseController
from services.file.FileService import FileService


class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
        self.file_service = FileService(self.app_settings)

    def get_project_path(self, project_id: str):
        return self.file_service.get_project_path(self.file_dir, project_id)
