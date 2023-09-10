import yaml
import streamlit as st
import streamlit_authenticator as stauth


def get_auth() -> stauth.Authenticate:
    with open("psychology_qa/auth_config.yaml") as file:
        auth_config = yaml.safe_load(file)

    return stauth.Authenticate(**auth_config)


def display_authentication_controls() -> None:
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
