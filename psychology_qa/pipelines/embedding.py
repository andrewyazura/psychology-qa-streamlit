from typing import TYPE_CHECKING

from haystack.nodes import EmbeddingRetriever

if TYPE_CHECKING:
    from haystack.document_stores.base import BaseDocumentStore


def get_embedding_retriever(
    document_store: "BaseDocumentStore" = None, top_k: int = 10
) -> EmbeddingRetriever:
    return EmbeddingRetriever(
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
        model_format="sentence_transformers",
        document_store=document_store,
        top_k=top_k,
    )
