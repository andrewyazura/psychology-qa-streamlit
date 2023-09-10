import streamlit as st
from haystack.nodes import SentenceTransformersRanker
from haystack.pipelines import Pipeline

from pipelines.embedding import get_embedding_retriever
from pipelines.pgvector_store import PgvectorStore
from config import ranker_model


@st.cache_resource(show_spinner=False)
def get_querying_pipeline() -> Pipeline:
    pipe = Pipeline()

    pipe.add_node(
        component=get_embedding_retriever(
            document_store=PgvectorStore(),
        ),
        name="Retriever",
        inputs=["Query"],
    )

    pipe.add_node(
        component=SentenceTransformersRanker(
            model_name_or_path=ranker_model,
        ),
        name="Ranker",
        inputs=["Retriever"],
    )

    return pipe
