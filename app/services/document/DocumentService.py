from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import logging

class DocumentService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_loader(self, file_path: str):
        file_extension = os.path.splitext(file_path)[-1]

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

    def get_content(self, file_path: str):
        file_loader = self.get_loader(file_path)
        if file_loader is None:
            raise ValueError(f"Unsupported file type: {file_path}")

        try:
            document = file_loader.load()
            return document
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            raise RuntimeError(f"Error loading file {file_path}")

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
