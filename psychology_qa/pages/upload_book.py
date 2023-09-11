import tempfile

import streamlit as st

from models import Author
from pages.base import BasePage


class UploadBookPage(BasePage):
    def _display(self) -> None:
        files_form = st.empty()
        author_options = Author.selectbox_options()

        with st.empty().form("files"):
            author_name = st.selectbox(
                "Select book's author", author_options.keys()
            )
            book_title = st.text_input("Enter book's title", max_chars=255)

            language = st.selectbox("Select book's language", ("en", "ru"))

            file = st.file_uploader(
                "Upload a book", type=["txt", "pdf", "md", "doc", "docx"]
            )

            form_submitted = st.form_submit_button(
                "Upload", use_container_width=True
            )

        if not form_submitted:
            st.stop()

        if not author_name:
            st.error("Author is required")
            st.stop()

        if not book_title:
            st.error("Book's title is required")
            st.stop()

        if not file:
            st.error("File is required")
            st.stop()

        files_form.empty()
        book = self.create_book(
            title=book_title, author_id=author_options[author_name]
        )

        with tempfile.NamedTemporaryFile(suffix=file.name) as temporary_file:
            temporary_file.write(file.read())

            self.process_data(
                {"language": language},
                {
                    "file_paths": [temporary_file.name],
                    "meta": {"book_id": book.id, "from_audio": True},
                },
            )

        st.success("Book added")


UploadBookPage().display()
