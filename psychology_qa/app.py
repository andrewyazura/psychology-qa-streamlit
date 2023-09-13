import streamlit as st

from views import ChatPage, LibraryPage, UploadBookPage

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Chat"

match st.session_state.selected_page:
    case "Chat":
        ChatPage().display()
    case "Library":
        LibraryPage().display()
    case "Upload a book":
        UploadBookPage().display()
