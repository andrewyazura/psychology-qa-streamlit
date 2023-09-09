import streamlit as st
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls

add_page_title()
show_pages_from_config()
display_authentication_controls()


def display_message(message: dict[str, str]) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    display_message(message)

if query := st.chat_input("Ask a psychology-related question"):
    message = {"role": "user", "content": query}

    display_message(message)
    st.session_state["messages"].append(message)
