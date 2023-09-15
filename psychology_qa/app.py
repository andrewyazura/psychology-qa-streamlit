import streamlit as st

from views import ChatView, LibraryView, UploadBookView

if "selected_view" not in st.session_state:
    st.session_state.selected_view = "Chat"

match st.session_state.selected_view:
    case "Chat":
        ChatView().display()

    case "Library":
        LibraryView().display()

    case "Upload a book":
        UploadBookView().display()
