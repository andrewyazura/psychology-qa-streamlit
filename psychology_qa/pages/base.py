import streamlit as st
from st_pages import add_page_title, show_pages_from_config

from authenticator import get_auth
from database import init_database


class BasePage:
    def __init__(self) -> None:
        pass

    def _display(self) -> None:
        raise NotImplementedError

    def display(self) -> None:
        self.display_authentication()

        show_pages_from_config()
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
