"""API routes and endpoints.

This package contains all API route definitions, organized by version:
v1/
  - Base routes (health check, version info)
  - Data routes (file upload, processing)
  - NLP routes (search, question answering)
"""

from .v1.base import base_router
from .v1.data import data_router
from .v1.nlp import nlp_router

__all__ = [
    'base_router',
    'data_router',
    'nlp_router'
]