from haystack.nodes import (
    DocxToTextConverter,
    FileTypeClassifier,
    MarkdownConverter,
    PDFToTextConverter,
    TextConverter,
)
from haystack.pipelines import Pipeline
from pipelines.custom_preprocessor import CustomPreProcessor
from pipelines.iterative_translator import CustomIterativeTranslator


def get_processing_pipeline(language: str) -> Pipeline:
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
    pipe.add_node(
        component=CustomPreProcessor(
            language=language,
            split_by="sentence",
            split_length=1,
            split_overlap=0,
            respect_sentence=False,
        ),
        name="PreProcessor",
        inputs=[
            "TextConverter",
            "PDFToTextConverter",
            "MarkdownConverter",
            "DocxToTextConverter",
        ],
    )

    if language != "en":
        pipe.add_node(
            component=CustomIterativeTranslator(
                from_language=language,
                to_language="en",
            ),
            name="Translator",
            inputs=["PreProcessor"],
        )

    return pipe
