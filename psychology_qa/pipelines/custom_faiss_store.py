from typing import TYPE_CHECKING
import streamlit as st
from haystack.nodes.base import BaseComponent
from pipelines.database import get_vector_store

if TYPE_CHECKING:
    from haystack.nodes.retriever.base import BaseRetriever
    from haystack.schema import Document


class CustomFAISSDocumentStore(BaseComponent):
    outgoing_edges = 1

    def __init__(self, retriever: "BaseRetriever") -> None:
        self.store = get_vector_store(**st.secrets["faiss"])
        self.retriever = retriever

    def run(self, documents: list["Document"]) -> tuple[dict, str]:
        self.store.write_documents(documents)
        self.store.update_embeddings(self.retriever)
        self.store.save(**st.secrets["faiss"])

        return {"documents": documents}, "output_1"

    def run_batch(self, documents: list["Document"]) -> tuple[dict, str]:
        return self.run(documents)
