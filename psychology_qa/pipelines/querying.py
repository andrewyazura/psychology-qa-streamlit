from haystack.nodes import EmbeddingRetriever
from haystack.pipelines import Pipeline

from config import embedding, prefixes, store_batch_size, translator
from pipelines.nodes import CustomBatchTranslator, PgvectorStore
from pipelines.nodes.custom_preprocessor import CustomPreProcessor
from utils import cache_resource


@cache_resource()
def get_querying_pipeline() -> Pipeline:
    pipe = Pipeline()

    last_node = "PreProcessor"
    pipe.add_node(
        component=CustomPreProcessor(prefix=prefixes["query"]),
        name=last_node,
        inputs=["Query"],
    )

    if translator["enabled"]:
        last_node = "Translator"
        pipe.add_node(
            component=CustomBatchTranslator(
                from_language="detect",
                to_language=translator["base_language"],
                batch_size=translator["batch_size"],
            ),
            name=last_node,
            inputs=["PreProcessor"],
        )

    pipe.add_node(
        component=EmbeddingRetriever(
            document_store=PgvectorStore(store_batch_size), **embedding
        ),
        name="Retriever",
        inputs=[last_node],
    )

    return pipe
