from typing import TYPE_CHECKING

import streamlit as st
from haystack.nodes import TransformersTranslator

if TYPE_CHECKING:
    from haystack.schema import Document


def translate(
    from_language: str, to_language: str, documents: list["Document"]
) -> list["Document"]:
    with st.spinner("Loading translator model..."):
        translator = TransformersTranslator(
            model_name_or_path=f"Helsinki-NLP/opus-mt-{from_language}-{to_language}",
        )

    bar = st.empty()
    bar.progress(0.0, text="Translating documents")

    for i, document in enumerate(documents):
        bar.progress(i / len(documents), text=f"Translating {i}/{len(documents)}")
        documents[i] = translator.translate(documents=[document])

    bar.progress(1.0, text="Done!")
    bar.empty()

    return documents
