import os
import tempfile
from typing import Any

import streamlit as st
from peewee import IntegrityError

from models import Author, Book
from views.base import BasePage


class UploadBookPage(BasePage):
    page_title = "Upload a book"
    page_icon = "📖"

    def _display(self) -> None:
        self.author_options = Author.select_box_options()

        self.author_name = st.selectbox(
            "Select book's author", self.author_options.keys()
        )
        self.book_title = st.text_input("Enter book's title", max_chars=255)
        self.language = st.selectbox("Select book's language", ("en", "ru"))

        book_tab, audiobook_tab = st.tabs(["Upload book", "Upload audiobook"])

        with book_tab:
            self._upload_book()

        with audiobook_tab:
            self._upload_audiobook()

    def _upload_book(self) -> None:
        file = st.file_uploader(
            "Upload a book", type=["txt", "pdf", "md", "doc", "docx"]
        )

        if not st.button("Upload book", use_container_width=True):
            return

        book = self._create_book()
        if not book:
            return

        if not file:
            st.error("File is required")
            return

        st.divider()

        with st.spinner("Processing data..."):
            with tempfile.NamedTemporaryFile(
                suffix=file.name
            ) as temporary_file:
                temporary_file.write(file.read())

                try:
                    self._process_data(
                        {"language": self.language},
                        {
                            "file_paths": [temporary_file.name],
                            "meta": {"book_id": book.id, "from_audio": True},
                        },
                    )

                except:
                    book.deep_delete()
                    raise

        st.success("Data uploaded", icon="📁")

    def _upload_audiobook(self) -> None:
        model_name = st.selectbox(
            "Select a whisper model",
            (
                "openai/whisper-tiny",
                "openai/whisper-base",
                "openai/whisper-small",
                "openai/whisper-medium",
                "openai/whisper-large",
                "openai/whisper-large-v2",
            ),
        )

        audio_files = st.file_uploader(
            "Upload audiobook files (multiple files allowed)",
            accept_multiple_files=True,
            type=["mp3", "m4a", "wav"],
        )

        if not st.button("Upload audiobook", use_container_width=True):
            return

        book = self._create_book()
        if not book:
            return

        if not audio_files:
            st.error("At least one file is required")
            return

        st.divider()

        with st.spinner("Processing data..."):
            with tempfile.TemporaryDirectory() as tempdirname:
                temporary_file_paths = []
                for audio in audio_files:
                    path = os.path.join(tempdirname, audio.name)
                    temporary_file_paths.append(path)

                    with open(path, "wb") as file:
                        file.write(audio.read())

                try:
                    self._process_data(
                        {
                            "language": self.language,
                            "whisper_model_name": model_name,
                        },
                        {
                            "file_paths": temporary_file_paths,
                            "meta": {"book_id": book.id, "from_audio": True},
                        },
                    )

                except:
                    book.deep_delete()
                    raise

        st.success("Data uploaded", icon="📁")

    def _process_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        from pipelines.indexing import get_indexing_pipeline

        pipeline = get_indexing_pipeline(**(init_kwargs or {}))
        return pipeline.run(**(run_kwargs or {}))

    def _create_book(self) -> Book:
        if not self.author_name:
            st.error("Select author")
            return

        if not self.book_title:
            st.error("Enter book's title")
            return

        try:
            return Book.create(
                author_id=self.author_options[self.author_name],
                title=self.book_title,
            )

        except IntegrityError:
            st.error("Book with this title already exists")
