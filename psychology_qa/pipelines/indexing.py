from haystack.nodes import (
    DocxToTextConverter,
    EmbeddingRetriever,
    FileTypeClassifier,
    MarkdownConverter,
    PDFToTextConverter,
    TextConverter,
)
from haystack.pipelines import Pipeline

from config import (
    embedding,
    prefixes,
    preprocessor,
    store_batch_size,
    translator,
    whisper_batch_size,
)
from pipelines.nodes import (
    CustomBatchTranslator,
    CustomPreProcessor,
    PgvectorStore,
    WhisperTranscriber,
)


def get_indexing_pipeline(
    language: str, whisper_model_name: str | None = None
) -> Pipeline:
    pipe = Pipeline()

    pipe.add_node(
        component=FileTypeClassifier(
            supported_types=["txt", "pdf", "md", "docx", "mp3"]
        ),
        name="FileTypeClassifier",
        inputs=["File"],
    )

    converters = [
        TextConverter,
        PDFToTextConverter,
        MarkdownConverter,
        DocxToTextConverter,
    ]
    converter_kwargs = {
        "valid_languages": [translator["base_language"], language]
    }

    for i, converter_class in enumerate(converters, start=1):
        pipe.add_node(
            component=converter_class(**converter_kwargs),
            name=converter_class.__name__,
            inputs=[f"FileTypeClassifier.output_{i}"],
        )

    if whisper_model_name:
        converters.append(WhisperTranscriber)

        pipe.add_node(
            component=WhisperTranscriber(
                model_name=whisper_model_name,
                language=language,
                batch_size=whisper_batch_size,
            ),
            name="WhisperTranscriber",
            inputs=["FileTypeClassifier.output_5"],
        )

    last_node = "PreProcessor"
    pipe.add_node(
        component=CustomPreProcessor(
            language=language, prefix=prefixes["passage"], **preprocessor
        ),
        name=last_node,
        inputs=[converter_class.__name__ for converter_class in converters],
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
        component=EmbeddingRetriever(**embedding),
        name="Retriever",
        inputs=[last_node],
    )

    pipe.add_node(
        component=PgvectorStore(batch_size=store_batch_size),
        name="DocumentStore",
        inputs=["Retriever"],
    )

    return pipe
