from haystack.nodes import SentenceTransformersRanker
from haystack.pipelines import Pipeline
from pipelines.database import get_vector_store
from pipelines.embedding import get_embedding_retriever


def get_querying_pipeline(top_k: int = 10) -> Pipeline:
    pipe = Pipeline()

    pipe.add_node(
        component=get_embedding_retriever(
            document_store=get_vector_store(),
            top_k=top_k,
        ),
        name="EmbeddingRetriever",
        inputs=["Query"],
    )

    pipe.add_node(
        component=SentenceTransformersRanker(
            model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2",
            top_k=top_k,
        ),
        name="SentenceTransformersRanker",
        inputs=["EmbeddingRetriever"],
    )

    return pipe
