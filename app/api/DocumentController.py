from .BaseController import BaseController
from .ProjectController import ProjectController
import os
import logging
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentController (BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id)

    def get_extension(self, file_name: str):
        return os.path.splitext(file_name)[-1]

    def get_loader(self, file_name: str):
        file_extension = self.get_extension(file_name)
        file_path = os.path.join(self.project_path, file_name)

        if not os.path.exists(file_path):
            return None

        if file_extension == '.pdf':
            return PyMuPDFLoader(file_path)
        elif file_extension == '.csv':
            return CSVLoader(file_path)
        elif file_extension == '.txt':
            return TextLoader(file_path, encoding='utf-8')
        else:
            return None

    def get_content(self, file_name: str):
        file_loader = self.get_loader(file_name)
        if file_loader is None:
            raise ValueError(f"Unsupported file type: {file_name}")

        try:
            document = file_loader.load()
            return document
        except Exception as e:
            self.logger.error(f"Error loading file {file_name}: {e}")
            raise RuntimeError(f"Error loading file {file_name}")

    def process_content(self, document: str, chunk_size: int = 100, chunk_overlap: int = 20):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            # Split the document into chunks
            document_texts = [rec.page_content for rec in document]
            document_metadata = [rec.metadata for rec in document]

            chunks = text_splitter.create_documents(
                texts=document_texts, metadatas=document_metadata
            )

            return chunks
        except Exception as e:
            self.logger.error(f"Error processing file content: {e}")
            raise RuntimeError(f"Error processing file content")
