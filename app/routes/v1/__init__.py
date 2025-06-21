"""API routes and endpoints.

This package contains all API route definitions, organized by version:
v1/
  - Base routes (health check, version info)
  - Document routes (document upload, prepare)
  - Knowledge Base routes (info, sync, search, answer)
"""

from .base import base_router
from .document_prepare import router as document_prepare_router
from .document_upload import router as document_upload_router
from .knowledgebase_sync import router as knowledgebase_sync_router
from .knowledgebase_info import router as knowledgebase_info_router
from .knowledgebase_search import router as knowledgebase_search_router
from .knowledgebase_answer import router as knowledgebase_answer_router

all_routers = [
    base_router,
    document_prepare_router,
    document_upload_router,
    knowledgebase_sync_router,
    knowledgebase_info_router,
    knowledgebase_search_router,
    knowledgebase_answer_router
]