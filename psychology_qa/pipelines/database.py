import os

import streamlit as st
from haystack.document_stores import FAISSDocumentStore


@st.cache_resource(show_spinner=False)
def get_vector_store(index_path: str, config_path: str) -> FAISSDocumentStore:
    if not os.path.exists(index_path):
        FAISSDocumentStore(
            sql_url=get_postgres_url(),
        ).save(index_path, config_path)

    return FAISSDocumentStore.load(index_path, config_path)


def get_postgres_url() -> str:
    """
    postgresql://[user[:password]@][host][:port][/dbname][?param1=value1&...]
    """

    return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
        **st.secrets["postgres"]
    )
