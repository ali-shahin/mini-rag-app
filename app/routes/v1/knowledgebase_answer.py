from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from schemas.nlp import SearchRequest
from repositories import ProjectRepo
from controllers import NlpController
import logging

logger = logging.getLogger(__name__)
    
router = APIRouter(
    prefix="/api/v1/knowledgebase",
    tags=["knowledgebase"]
)

# /api/v1/knowledgebase/answer/{project_id}
@router.post("/answer/{project_id}")
async def answer_knowledgebase(request: Request, project_id: str, request_data: SearchRequest):
    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    nlp_controller = NlpController(request.app.vector_db_client, request.app.generation_client, request.app.embedding_client)

    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )
    
    answer = await nlp_controller.answer_query(project.project_id, request_data.query, request_data.limit)
    if not answer:
        return JSONResponse(status.HTTP_400_BAD_REQUEST, content={"message": "No results found."})
        
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Data retrieved.", "answer": answer})