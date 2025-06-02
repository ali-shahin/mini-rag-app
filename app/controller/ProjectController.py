from .BaseController import BaseController


class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        return self.file_service.get_project_path(project_id)
