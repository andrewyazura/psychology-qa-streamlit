import streamlit as st
from haystack.nodes import (
    DocxToTextConverter,
    FileTypeClassifier,
    MarkdownConverter,
    PDFToTextConverter,
    TextConverter,
)
from haystack.pipelines import Pipeline
from pipelines.custom_faiss_store import CustomFAISSDocumentStore
from pipelines.custom_preprocessor import CustomPreProcessor
from pipelines.embedding import get_embedding_retriever
from pipelines.iterative_translator import CustomIterativeTranslator


@st.cache_resource(show_spinner=False)
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

    last_node = "PreProcessor"
    pipe.add_node(
        component=CustomPreProcessor(
            language=language,
            split_by="sentence",
            split_length=3,
            split_overlap=1,
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

    if language != "en":
        last_node = "Translator"
        pipe.add_node(
            component=CustomIterativeTranslator(
                from_language=language,
                to_language="en",
            ),
            name=last_node,
            inputs=["PreProcessor"],
        )

    pipe.add_node(
        component=CustomFAISSDocumentStore(
            retriever=get_embedding_retriever()
        ),
        name="FAISSDocumentStore",
        inputs=[last_node],
    )

    return pipe
