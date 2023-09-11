import os
import tempfile

import streamlit as st

from models import Author
from pages.base import BasePage


class UploadAudioPage(BasePage):
    def _display(self) -> None:
        files_form = st.empty()
        author_options = Author.selectbox_options()

        with files_form.form("audio_files"):
            author_name = st.selectbox(
                "Select audiobook's author", author_options
            )
            book_title = st.text_input(
                "Enter audiobook's title", max_chars=255
            )

            language = st.selectbox(
                "Select language of the audiobook", ("en", "ru")
            )
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
                type=["wav", "mp3", "m4a"],
            )

            if not st.form_submit_button("Upload", use_container_width=True):
                st.stop()

        if not author_name:
            st.error("Author is required")
            st.stop()

        if not book_title:
            st.error("Book is requied")
            st.stop()

        if not audio_files:
            st.error("Upload at least one file")
            st.stop()

        files_form.empty()
        book = self.create_book(
            title=book_title, author_id=author_options[author_name]
        )

        with tempfile.TemporaryDirectory() as tempdirname:
            temporary_file_paths = []
            for audio in audio_files:
                path = os.path.join(tempdirname, audio.name)
                temporary_file_paths.append(path)

                with open(path, "wb") as file:
                    file.write(audio.read())

            self.process_data(
                {"language": language, "whisper_model_name": model_name},
                {
                    "file_paths": temporary_file_paths,
                    "meta": {"book_id": book.id, "from_audio": True},
                },
            )

        st.success("Book added")


UploadAudioPage().display()
