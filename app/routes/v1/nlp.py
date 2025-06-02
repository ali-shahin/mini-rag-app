from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from schemas.nlp import PushRequest, SearchRequest
from repositories import ProjectRepo, DataChunkRepo
from api import NlpController
import logging

logger = logging.getLogger(__name__)
    
nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["nlp"])


@nlp_router.post("/index-push/{project_id}")
async def index_data(request: Request, project_id: str, request_data: PushRequest):

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

@nlp_router.get("/index-pull/{project_id}")
async def pull_data(request: Request, project_id: str):
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

@nlp_router.post("/search/{project_id}")
async def search_data(request: Request, project_id: str, request_data: SearchRequest):
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
    
    results = [dict(result) for result in results]
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Data retrieved.", "results": results})


@nlp_router.post("/answer/{project_id}")
async def answer_query(request: Request, project_id: str, request_data: SearchRequest):
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