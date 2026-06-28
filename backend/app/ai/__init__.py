"""
SomaHub AI Module — RAG, OCR, Embeddings, Vector Store, and Chat.
"""

from app.ai.config import AISettings, get_ai_settings
from app.ai.ollama_client import OllamaClient
from app.ai.embeddings import EmbeddingService
from app.ai.vectorstore import IVectorStore, ChromaVectorStore, get_vector_store
from app.ai.text_extractor import TextExtractor
from app.ai.chunker import TextChunker
from app.ai.ingestion import IngestionPipeline
from app.ai.ocr import OCRPipeline
from app.ai.rag import RAGPipeline
from app.ai.app_knowledge import AppKnowledgeBase
from app.ai.book_indexer import BookIndexer

__all__ = [
    "AISettings",
    "get_ai_settings",
    "OllamaClient",
    "EmbeddingService",
    "IVectorStore",
    "ChromaVectorStore",
    "get_vector_store",
    "TextExtractor",
    "TextChunker",
    "IngestionPipeline",
    "OCRPipeline",
    "RAGPipeline",
    "AppKnowledgeBase",
    "BookIndexer",
]
