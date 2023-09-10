from haystack.nodes import (
    DocxToTextConverter,
    FileTypeClassifier,
    MarkdownConverter,
    PDFToTextConverter,
    TextConverter,
)
from haystack.pipelines import Pipeline

from config import store_batch_size, translator
from pipelines.batch_translator import CustomBatchTranslator
from pipelines.custom_preprocessor import CustomPreProcessor
from pipelines.embedding import get_embedding_retriever
from pipelines.pgvector_store import PgvectorStore
from utils import cache_resource


@cache_resource()
def get_indexing_pipeline(language: str) -> Pipeline:
    converter_kwargs = {
        "remove_numeric_tables": True,
        "valid_languages": [language],
    }

    pipe = Pipeline()

    pipe.add_node(
        component=FileTypeClassifier(),
        name="FileTypeClassifier",
        inputs=["File"],
    )

    pipe.add_node(
        component=TextConverter(**converter_kwargs),
        name="TextConverter",
        inputs=["FileTypeClassifier.output_1"],
    )

    pipe.add_node(
        component=PDFToTextConverter(**converter_kwargs),
        name="PDFToTextConverter",
        inputs=["FileTypeClassifier.output_2"],
    )

    pipe.add_node(
        component=MarkdownConverter(**converter_kwargs),
        name="MarkdownConverter",
        inputs=["FileTypeClassifier.output_3"],
    )

    pipe.add_node(
        component=DocxToTextConverter(**converter_kwargs),
        name="DocxToTextConverter",
        inputs=["FileTypeClassifier.output_4"],
    )

    last_node = "PreProcessor"
    pipe.add_node(
        component=CustomPreProcessor(
            language=language,
            split_by="sentence",
            split_length=1,
            split_overlap=0,
            respect_sentence=False,
        ),
        name=last_node,
        inputs=[
            "TextConverter",
            "PDFToTextConverter",
            "MarkdownConverter",
            "DocxToTextConverter",
        ],
    )

    if translator["enabled"] and language != translator["base_language"]:
        last_node = "Translator"
        pipe.add_node(
            component=CustomBatchTranslator(
                from_language=language,
                to_language=translator["base_language"],
                batch_size=translator["batch_size"],
            ),
            name=last_node,
            inputs=["PreProcessor"],
        )

    pipe.add_node(
        component=get_embedding_retriever(),
        name="Retriever",
        inputs=[last_node],
    )

    pipe.add_node(
        component=PgvectorStore(batch_size=store_batch_size),
        name="DocumentStore",
        inputs=["Retriever"],
    )

    return pipe
