from abc import ABC, abstractmethod

import streamlit as st

from authenticator import get_auth
from database import init_database


class BasePage(ABC):
    page_title: str
    page_icon: str

    @abstractmethod
    def _display(self) -> None:
        ...

    def display(self) -> None:
        self._display_page_title()
        self._display_authentication()

        init_database()

        self._display()

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

    def _display_page_title(self):
        st.set_page_config(
            page_title=self.page_title, page_icon=self.page_icon
        )
        st.header(f"{self.page_icon} {self.page_title}", divider="rainbow")
