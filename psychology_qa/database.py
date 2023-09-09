import streamlit as st
from haystack.document_stores import SQLDocumentStore, FAISSDocumentStore


def get_database() -> SQLDocumentStore:
    return SQLDocumentStore(
        url=get_database_connection_string(),
        index="document",
        label_index="label",
        duplicate_documents="overwrite",
    )


def get_database_connection_string() -> str:
    """
    postgresql://[user[:password]@][host][:port][/dbname][?param1=value1&...]
    """

    return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
        **st.secrets["postgres"]
    )


def get_vector_store() -> FAISSDocumentStore:
    return FAISSDocumentStore()
