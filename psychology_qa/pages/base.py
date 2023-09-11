from typing import Any

import streamlit as st
from peewee import IntegrityError
from st_pages import add_page_title, show_pages_from_config

from authenticator import get_auth
from database import init_database
from models import Book


class BasePage:
    def __init__(self) -> None:
        pass

    def _display(self) -> None:
        raise NotImplementedError

    def display(self) -> None:
        show_pages_from_config()
        self.display_authentication()
        add_page_title()
        init_database()

        self._display()

    def display_authentication(self) -> None:
        authenticator = get_auth()
        name, auth_status, _ = authenticator.login("Login", "main")

        if auth_status:
            st.sidebar.header(f"Hi, {name}!")
            authenticator.logout("Logout", "sidebar")

        elif auth_status is False:
            st.error("Username/password is incorrect")
            st.stop()

        elif auth_status is None:
            st.stop()

    def create_book(self, **kwargs) -> Book:
        try:
            return Book.create(**kwargs)

        except IntegrityError:
            st.error("Failed to add a book")
            st.stop()

    def process_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        with st.spinner("Processing data..."):
            from pipelines.indexing import get_indexing_pipeline

            pipeline = get_indexing_pipeline(**(init_kwargs or {}))
            return pipeline.run(**(run_kwargs or {}))

    def query_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        with st.spinner("Searching for answers..."):
            from pipelines.querying import get_querying_pipeline

            pipeline = get_querying_pipeline(**(init_kwargs or {}))
            return pipeline.run(**(run_kwargs or {}))
