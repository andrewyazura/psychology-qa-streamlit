import logging
import os
import tempfile
import time

import streamlit as st
from humanfriendly import format_timespan
from peewee import IntegrityError

from models import Author, Book
from views.base import BaseView

logger = logging.getLogger(__name__)


class UploadBookView(BaseView):
    view_title = "Upload a book"
    view_icon = "📖"

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
        files = st.file_uploader(
            "Upload files (multiple allowed)",
            accept_multiple_files=True,
            type=["txt", "pdf", "md", "doc", "docx"],
        )

        if not st.button("Upload book", use_container_width=True):
            return

        self._process_data(files)

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
            "Upload audio files (multiple allowed)",
            accept_multiple_files=True,
            type=["mp3"],
        )

        if not st.button("Upload audiobook", use_container_width=True):
            return

        self._process_data(audio_files, model_name)

    def _process_data(
        self, uploaded_files: list, whisper_model_name: str | None = None
    ) -> None:
        book = self._create_book()

        if not book:
            return

        if not uploaded_files:
            st.error("At least one file is required")
            return

        st.divider()
        start_time = time.time()

        with st.status(
            "Processing data...", state="running", expanded=True
        ) as status:
            with tempfile.TemporaryDirectory() as tempdirname:
                temporary_file_paths = []

                for uploaded_file in uploaded_files:
                    path = os.path.join(tempdirname, uploaded_file.name)
                    temporary_file_paths.append(path)

                    with open(path, "wb") as file:
                        file.write(uploaded_file.read())

                try:
                    logger.info("Loading pipeline...")
                    st.caption("Loading pipeline...")

                    from pipelines.indexing import get_indexing_pipeline

                    pipeline = get_indexing_pipeline(
                        language=self.language,
                        whisper_model_name=whisper_model_name,
                    )

                    diff = self._get_formatted_timespan(start_time)

                    logger.info(f"Finished loading in {diff}")
                    logger.info("Running pipeline...")

                    st.caption(f"Finished loading in {diff}")
                    st.caption("Running pipeline...")

                    pipeline.run(
                        file_paths=temporary_file_paths,
                        meta={"book_id": book.id, "from_audio": True},
                    )

                except:
                    diff = self._get_formatted_timespan(start_time)
                    status.update(
                        label=f"Unexpected error. Finished in {diff}",
                        state="error",
                        expanded=False,
                    )

                    book.deep_delete()
                    raise

            diff = self._get_formatted_timespan(start_time)
            logger.info(f"Data processed. Finished in {diff}")

            status.update(
                label=f"Data processed. Finished in {diff}",
                state="complete",
                expanded=False,
            )

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
                language=self.language,
            )

        except IntegrityError:
            st.error("Book with this title already exists")

    @staticmethod
    def _get_formatted_timespan(start_time: float) -> str:
        return format_timespan(time.time() - start_time)
