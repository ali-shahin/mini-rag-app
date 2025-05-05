from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse
from core.config import get_settings, Settings
from api import DataController, DocumentController
import aiofiles
import logging
from schemas.data import DataDocumentRequest


logger = logging.getLogger(__name__)

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"])


@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile = File(...),
                      app_settings: Settings = Depends(get_settings)):

    data_controller = DataController()

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

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "File uploaded successfully",
                 "file_name": file_name}
    )


@data_router.post("/process/{project_id}")
async def process_data(project_id: str, document_request: DataDocumentRequest):

    document_controller = DocumentController(project_id)

    file_name = document_request.file_name
    chunk_size = document_request.chunk_size
    chunk_overlap = document_request.chunk_overlap

    try:
        # Load the document
        document = document_controller.get_content(file_name)
        if not document:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": f"File {file_name} not found."}
            )

        # Process the content
        chunks = document_controller.process_content(
            document)
        if not chunks:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Failed to process file."}
            )

        return chunks
    except Exception as e:
        logger.error(f"Error processing file {file_name}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Error processing file {file_name}"}
        )
