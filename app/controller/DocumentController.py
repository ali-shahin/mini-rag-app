from .BaseController import BaseController
from services.document.DocumentService import DocumentService
from services.file.FileService import FileService

import os
import logging


class DocumentController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.project_id = project_id
        self.file_service = FileService(settings=self.app_settings)
        self.document_service = DocumentService()

    def get_extension(self, file_name: str):
        return os.path.splitext(file_name)[-1]

    def get_content(self, file_name: str):
        project_path = self.file_service.get_project_path(self.project_id)
        file_path = os.path.join(project_path, file_name)
        return self.document_service.get_content(file_path)

    def process_content(self, document: str, chunk_size: int = 100, chunk_overlap: int = 20):
        return self.document_service.process_content(document, chunk_size, chunk_overlap)
