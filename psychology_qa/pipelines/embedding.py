from typing import TYPE_CHECKING

from haystack.nodes import EmbeddingRetriever

from config import embedding_model

if TYPE_CHECKING:
    from haystack.nodes.base import BaseComponent


def get_embedding_retriever(
    document_store: "BaseComponent" = None,
) -> EmbeddingRetriever:
    return EmbeddingRetriever(
        embedding_model=embedding_model,
        model_format="sentence_transformers",
        document_store=document_store,
    )
