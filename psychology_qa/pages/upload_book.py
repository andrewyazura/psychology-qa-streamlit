import tempfile
from typing import TYPE_CHECKING

import streamlit as st
from peewee import PeeweeException
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls
from constants import LANGUAGES
from database import init_database
from models import Author, Book

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()
init_database()

AUTHORS_NAME_TO_ID = {author.name: author.id for author in Author.select()}

files_form = st.empty()
with st.empty().form("files"):
    author_name = st.selectbox(
        "Select book's author", AUTHORS_NAME_TO_ID.keys()
    )
    book_title = st.text_input("Enter book's title", max_chars=255)

    language = st.selectbox("Select book's language", LANGUAGES)

    file: "UploadedFile" = st.file_uploader(
        "Upload a book", type=["txt", "pdf", "md", "doc", "docx"]
    )

    form_submitted = st.form_submit_button("Upload", use_container_width=True)

if not form_submitted:
    st.stop()

if author_name is None:
    st.error("Author is required")
    st.stop()

if book_title is None or book_title.strip() == "":
    st.error("Book's title is required")
    st.stop()

if file is None:
    st.error("File is required")
    st.stop()

files_form.empty()

try:
    book = Book.create(
        author_id=AUTHORS_NAME_TO_ID[author_name], title=book_title.strip()
    )

except PeeweeException:
    st.error("Failed to add a book")
    st.stop()

with tempfile.NamedTemporaryFile(suffix=file.name) as temp:
    temp.write(file.read())

    with st.spinner("Processing text..."):
        from pipelines.indexing import get_indexing_pipeline

        pipe = get_indexing_pipeline(language)
        result: dict = pipe.run(
            file_paths=[temp.name], meta={"book_id": book.id}
        )

    st.success(f"Book {book_title} successfully added")
