from abc import ABC, abstractmethod

import streamlit as st

from authenticator import get_auth
from database import init_database


class BaseView(ABC):
    view_title: str
    view_icon: str

    @abstractmethod
    def _display(self) -> None:
        ...

    def display(self) -> None:
        self._display_view_title()
        self._display_authentication()
        self._view_selector()

        self.database = init_database()

        self._display()

    def _display_view_title(self) -> None:
        st.set_page_config(
            page_title=self.view_title, page_icon=self.view_icon
        )
        st.header(f"{self.view_icon} {self.view_title}", divider="rainbow")

    def _display_authentication(self) -> None:
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

    def _view_selector(self) -> None:
        selected_view = st.sidebar.radio(
            "Select a page", ("Chat", "Library", "Upload a book")
        )

        if selected_view != st.session_state.get("selected_view", "Chat"):
            st.session_state.selected_view = selected_view
            st.experimental_rerun()
