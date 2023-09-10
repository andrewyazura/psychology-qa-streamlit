from typing import TYPE_CHECKING

from haystack.nodes import EmbeddingRetriever

if TYPE_CHECKING:
    from haystack.nodes.base import BaseComponent


def get_embedding_retriever(
    document_store: "BaseComponent" = None,
) -> EmbeddingRetriever:
    return EmbeddingRetriever(
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
        model_format="sentence_transformers",
        document_store=document_store,
    )
