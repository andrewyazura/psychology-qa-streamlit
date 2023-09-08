import streamlit as st
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls

add_page_title()
show_pages_from_config()
display_authentication_controls()

query = st.chat_input("Ask a psychology-related question")

if not query:
    st.stop()

st.write(query)
