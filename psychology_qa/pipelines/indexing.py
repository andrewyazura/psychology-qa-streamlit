from haystack.nodes import (
    DocxToTextConverter,
    FileTypeClassifier,
    MarkdownConverter,
    PDFToTextConverter,
    TransformersTranslator,
    TextConverter,
)
from haystack.pipelines import Pipeline
from pipelines.preprocessor import CustomPreProcessor


def get_indexing_pipeline(language: str) -> Pipeline:
    converter_kwargs = {
        "progress_bar": False,
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
    pipe.add_node(
        component=CustomPreProcessor(language=language),
        name="CustomPreProcessor",
        inputs=[
            "TextConverter",
            "PDFToTextConverter",
            "MarkdownConverter",
            "DocxToTextConverter",
        ],
    )

    if language not in ("en",):
        pipe.add_node(
            component=TransformersTranslator(
                model_name_or_path=f"Helsinki-NLP/opus-mt-{language}-en",
                use_gpu=False,
            ),
            name="TransformersTranslator",
            inputs=["CustomPreProcessor"],
        )

    return pipe
