import os

import streamlit as st
from haystack.document_stores import FAISSDocumentStore


def get_vector_store() -> FAISSDocumentStore:
    faiss_config = {
        "index_path": "./data/faiss_index",
        "config_path": "./data/faiss_index.json",
    }

    if not os.path.exists(faiss_config["index_path"]):
        FAISSDocumentStore(
            sql_url=get_postgres_url(),
        ).save(**faiss_config)

    return FAISSDocumentStore.load(**faiss_config)


def get_postgres_url() -> str:
    """
    postgresql://[user[:password]@][host][:port][/dbname][?param1=value1&...]
    """

    return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
        **st.secrets["postgres"]
    )
