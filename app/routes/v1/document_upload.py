from fastapi import APIRouter, UploadFile, File, Request, Depends, status
from fastapi.responses import JSONResponse
import aiofiles
import logging
import os
from core.config import get_settings, Settings
from api import DataController
from repositories import ProjectRepo, AssetRepo
from models import Asset

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Documents"])

# /api/v1/projects/{project_id}/documents/upload
@router.post("/projects/{project_id}/documents/upload")
async def upload_document(request: Request, project_id: str, document: UploadFile = File(...),
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

    # Validate the document
    is_valid, message = data_controller.validate_file(document)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": message}
        )

    # Save the document to the server
    chunk_size = app_settings.FILE_CHUNK_SIZE
    file_path, file_name = data_controller.get_file_path(
        project_id, document.filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while True:
                chunk = await document.read(chunk_size)
                if not chunk:
                    break
                await out_file.write(chunk)
    except Exception as e:
        logger.error(f"Failed to save Document. Error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Failed to save Document."}
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
        content={"message": "Document uploaded successfully",
                 "file_id": str(_asset.id),
                 "project_id": project.project_id
                 }
    )