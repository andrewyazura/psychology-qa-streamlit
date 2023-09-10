from typing import TYPE_CHECKING

import streamlit as st
from playhouse.postgres_ext import PostgresqlExtDatabase

from models import Author, Book, EmbeddingDocument, MetaDocument

if TYPE_CHECKING:
    from peewee import DatabaseProxy


def init_database() -> "DatabaseProxy":
    from models import database_proxy

    database = get_database()
    database_proxy.initialize(database)
    database_proxy.create_tables(
        [Author, Book, EmbeddingDocument, MetaDocument]
    )

    return database_proxy


@st.cache_resource(show_spinner=False)
def get_database() -> PostgresqlExtDatabase:
    return PostgresqlExtDatabase(**st.secrets["postgres"])
