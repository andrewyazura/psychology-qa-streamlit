from haystack.nodes import SentenceTransformersRanker
from haystack.pipelines import Pipeline

from config import ranker_model, store_batch_size, translator
from pipelines.batch_translator import CustomBatchTranslator
from pipelines.embedding import get_embedding_retriever
from pipelines.pgvector_store import PgvectorStore
from utils import cache_resource


@cache_resource()
def get_querying_pipeline() -> Pipeline:
    pipe = Pipeline()
    last_node = "Query"

    if translator["enabled"]:
        last_node = "Translator"
        pipe.add_node(
            component=CustomBatchTranslator(
                from_language="detect",
                to_language=translator["base_language"],
                batch_size=translator["batch_size"],
            ),
            name=last_node,
            inputs=["Query"],
        )

    pipe.add_node(
        component=get_embedding_retriever(
            document_store=PgvectorStore(store_batch_size)
        ),
        name="Retriever",
        inputs=[last_node],
    )

    pipe.add_node(
        component=SentenceTransformersRanker(model_name_or_path=ranker_model),
        name="Ranker",
        inputs=["Retriever"],
    )

    return pipe
