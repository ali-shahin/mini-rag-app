from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
import logging

from repositories import ProjectRepo
from api import NlpController

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/knowledgebase",
    tags=["Knowledge Base"])

@router.get("/info/{project_id}")
async def get_knowledgebase_info(request: Request, project_id: str):
    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    nlp_controller = NlpController(request.app.vector_db_client, request.app.generation_client, request.app.embedding_client)

    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )
    
    collection_info = await nlp_controller.get_vector_collection(project.project_id)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Data retrieved.", "collection_info": collection_info})
