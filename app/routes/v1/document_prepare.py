from fastapi import APIRouter,Request, status
from fastapi.responses import JSONResponse
import logging

from api import DocumentController
from repositories import ProjectRepo, AssetRepo, DataChunkRepo
from schemas.data import DataDocumentRequest
from models import DataChunk


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Documents"])

# /api/v1/projects/{project_id}/documents/process
@router.post("/projects/{project_id}/documents/process")
async def prepare_documents(request: Request, project_id: str, document_request: DataDocumentRequest):

    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    data_chunk_repo = await DataChunkRepo.create_instance(request.app.db_client)
    asset_repo = await AssetRepo.create_instance(request.app.db_client)
    document_controller = DocumentController(project_id)

    chunk_size = document_request.chunk_size
    chunk_overlap = document_request.chunk_overlap
    do_reset = document_request.do_reset

    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )

    project_documents = await asset_repo.get_project_assets(project.id, "file")
    if not project_documents:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} has no documents."}
        )

    # Delete existing chunks if required
    if do_reset == 1:
        await data_chunk_repo.delete_chunks(project.id)

    no_of_chunks = 0
    no_of_documents = 0

    for document in project_documents:
        try:
            # Load the document
            _document = document_controller.get_content(document.asset_name)
            if _document is None:
                logger.error(f"Failed to load document {document.asset_name}")
                continue

            # Process the content
            chunks = document_controller.process_content(
                _document, chunk_size, chunk_overlap)
            if not chunks:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"message": "Failed to process document."}
                )

            # Save the chunks to the database
            chunk_processed = [
                DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=index + 1,
                    chunk_project_id=project.id,
                    chunk_asset_id=document.id
                )
                for index, chunk in enumerate(chunks)
            ]

            no_of_chunks += await data_chunk_repo.insert_chunks(chunk_processed)
            no_of_documents += 1
            if not no_of_chunks:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"message": "Failed to save chunks."}
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Document processed successfully",
                         "inserted chunks": no_of_chunks,
                         "processed documents": no_of_documents,
                         }
            )
        except Exception as e:
            logger.error(f"Error processing document {document.file_name}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Error processing document {document.file_name}"}
            )
