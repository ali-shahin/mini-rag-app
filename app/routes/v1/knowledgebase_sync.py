from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
import logging

from schemas.nlp import PushRequest
from repositories import ProjectRepo, DataChunkRepo
from api import NlpController

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/knowledgebase",
    tags=["Knowledge Base"])

# /api/v1/knowledgebase/sync/{project_id}
@router.post("/sync/{project_id}")
async def sync_knowledgebase(request: Request, project_id: str, request_data: PushRequest):

    project_repo = await ProjectRepo.create_instance(request.app.db_client)
    data_chunk_repo = await DataChunkRepo.create_instance(request.app.db_client)
    nlp_controller = NlpController(request.app.vector_db_client, request.app.generation_client, request.app.embedding_client)

    project = await project_repo.get_or_create_project(project_id)
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project {project_id} not found."}
        )

    page=1
    idx=0
    inserted_count = 0
    has_more = True

    while has_more:
        data_chunks = await data_chunk_repo.get_project_chunks(project.id, page)
        if not data_chunks or len(data_chunks) == 0:
            has_more = False
            break

        chunk_ids = list(range(idx, idx+len(data_chunks)))
        idx += len(data_chunks)

        await nlp_controller.index_data(project.project_id, data_chunks, chunk_ids, request_data.do_reset)
        page += 1
        inserted_count += len(data_chunks)
    

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Data indexed.", "inserted_count": inserted_count})