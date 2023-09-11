from haystack.nodes import EmbeddingRetriever, SentenceTransformersRanker
from haystack.pipelines import Pipeline

from config import embedding_model, ranker_model, store_batch_size, translator
from pipelines.nodes import CustomBatchTranslator, PgvectorStore
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
        component=EmbeddingRetriever(
            embedding_model=embedding_model,
            model_format="sentence_transformers",
            document_store=PgvectorStore(store_batch_size),
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
