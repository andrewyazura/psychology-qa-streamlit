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
    messages = [{"role": "user", "content": query}]

    with st.spinner("Searching for answers..."):
        from pipelines.querying import get_querying_pipeline

        pipe = get_querying_pipeline(top_k=3)
        documents = pipe.run(query=query)

    if not documents:
        messages.append({"role": "assistant", "content": "Nothing found..."})

    for document in documents:
        messages.append({"role": "assistant", "content": document.content})

    for message in messages:
        display_message(message)

    st.session_state["messages"].extend(messages)
