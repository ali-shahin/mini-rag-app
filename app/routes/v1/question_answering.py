from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
# from core.config import get_settings
from schemas.nlp import PushRequest, SearchRequest
from repositories import ProjectRepo, DataChunkRepo
from api import NlpController
import logging

logger = logging.getLogger(__name__)
    
router = APIRouter(
    prefix="/api/v1/knowledgebase",
    tags=["knowledgebase"]
)

# /api/v1/knowledgebase/search/{project_id}
@router.post("/search/{project_id}")
async def search_knowledgebase(request: Request, project_id: str, request_data: SearchRequest):
    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    nlp_controller = NlpController(request.app.vector_db_client, request.app.generation_client, request.app.embedding_client)

    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )
    
    results = await nlp_controller.search_vector_collection(project.project_id, request_data.query, request_data.limit)
    if not results:
        return JSONResponse(status.HTTP_400_BAD_REQUEST, content={"message": "No results found."})
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Data retrieved.", "results": results})