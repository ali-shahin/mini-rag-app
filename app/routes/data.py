from fastapi import APIRouter, Depends, UploadFile, File, status, Request
from fastapi.responses import JSONResponse
from core.config import get_settings, Settings
from api import DataController, DocumentController
import aiofiles
import logging
import os
from schemas.data import DataDocumentRequest
from repositories import ProjectRepo, DataChunkRepo, AssetRepo
from models import DataChunk, Asset


logger = logging.getLogger(__name__)

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile = File(...),
                      app_settings: Settings = Depends(get_settings)):

    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    asset_repo = await AssetRepo.create_instance(request.app.db_client)
    data_controller = DataController()

    # Get the project
    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )

    # Validate the file
    is_valid, message = data_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": message}
        )

    # Save the file to the server
    chunk_size = app_settings.FILE_CHUNK_SIZE
    file_path, file_name = data_controller.get_file_path(
        project_id, file.filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save file. Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Failed to save file."}
        )

    # Save the file to the database
    asset = Asset(
        asset_project_id=project.id,
        asset_type="file",
        asset_name=file_name,
        asset_size=os.path.getsize(file_path)
    )
    _asset = await asset_repo.create_asset(asset)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "File uploaded successfully",
                 "file_id": str(_asset.id),
                 "project_id": project.project_id
                 }
    )


@data_router.post("/process/{project_id}")
async def process_data(request: Request, project_id: str, document_request: DataDocumentRequest):

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

    project_files = await asset_repo.get_project_assets(project.id, "file")
    if not project_files:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} has no files."}
        )

    # Delete existing chunks if required
    if do_reset == 1:
        await data_chunk_repo.delete_chunks(project.id)

    no_of_chunks = 0
    no_of_files = 0

    for file in project_files:
        try:
            # Load the document
            document = document_controller.get_content(file.asset_name)
            if document is None:
                logger.error(f"Failed to load file {file.asset_name}")
                continue

            # Process the content
            chunks = document_controller.process_content(
                document, chunk_size, chunk_overlap)
            if not chunks:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"message": "Failed to process file."}
                )

            # Save the chunks to the database
            chunk_processed = [
                DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=index + 1,
                    chunk_project_id=project.id,
                    chunk_asset_id=file.id
                )
                for index, chunk in enumerate(chunks)
            ]

            no_of_chunks += await data_chunk_repo.insert_chunks(chunk_processed)
            no_of_files += 1
            if not no_of_chunks:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"message": "Failed to save chunks."}
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "File processed successfully",
                         "inserted chunks": no_of_chunks,
                         "processed files": no_of_files,
                         }
            )
        except Exception as e:
            logger.error(f"Error processing file {file.file_name}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Error processing file {file.file_name}"}
            )
