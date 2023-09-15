import streamlit as st

from log_config import init_logging
from views import ChatView, LibraryView, UploadBookView

init_logging()

if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Chat"

match st.session_state.selected_view:
    case "Chat":
        ChatView().display()

    case "Library":
        LibraryView().display()

    case "Upload a book":
        UploadBookView().display()
