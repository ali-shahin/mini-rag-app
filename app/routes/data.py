from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
from core.config import get_settings, Settings
from api import DataController
import aiofiles
import logging
from schemas.data import DataProcessRequest


logger = logging.getLogger(__name__)

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile = File(...),
                      app_settings: Settings = Depends(get_settings)):

    # Validate the file
    is_valid, message = DataController().validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": message}
        )

    # Save the file to the server
    chunk_size = app_settings.FILE_CHUNK_SIZE
    file_path, file_name = DataController().get_file_path(project_id, file.filename)

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

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "File uploaded successfully",
                 "file_name": file_name}
    )


@data_router.post("/process/{project_id}")
async def process_data(project_id: str, process_request: DataProcessRequest):
    file_id = process_request.file_id
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Processing data for project {project_id} with file ID {file_id}"}
    )
