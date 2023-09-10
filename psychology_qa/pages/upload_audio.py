import tempfile
from typing import TYPE_CHECKING

import librosa as lr
import streamlit as st
from peewee import PeeweeException
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls
from constants import LANGUAGES, SAMPLE_RATE, WHISPER_MODELS
from database import init_database
from models import Author, Book

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()
init_database()

AUTHORS_NAME_TO_ID = {
    author.name: author.id for author in Author.select(Author.name)
}

files_form = st.empty()
with files_form.form("files"):
    author_name = st.selectbox(
        "Select book's author", AUTHORS_NAME_TO_ID.keys()
    )
    book_title = st.text_input("Enter book's title", max_chars=255)

    language = st.selectbox("Select language of the audiobook", LANGUAGES)
    model_name = st.selectbox("Select a whisper model", WHISPER_MODELS)

    files: list["UploadedFile"] = st.file_uploader(
        "Upload an audiobook (multiple files allowed)",
        accept_multiple_files=True,
        type=["wav", "mp3", "m4a"],
    )

    form_submitted = st.form_submit_button("Upload", use_container_width=True)

if not form_submitted:
    st.stop()

if author_name is None:
    st.error("Author is required")
    st.stop()

if book_title is None or book_title.strip == "":
    st.error("Book's title is required")
    st.stop()

if not files:
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

with st.spinner("Loading Whisper model..."):
    from pipelines.whisper import get_whisper_pipeline

    whisper = get_whisper_pipeline(model_name)

bar = st.empty()
bar.progress(0.0, text="Transcribing files")

with tempfile.NamedTemporaryFile(suffix=".txt") as temp:
    for i, file in enumerate(reversed(files)):
        bar.progress(i / len(files), text=f"Transcribing {i}/{len(files)}")
        audio, _ = lr.load(file, sr=SAMPLE_RATE)

        result = whisper(
            audio,
            generate_kwargs={
                "task": "transcribe",
                "language": f"<|{language}|>",
            },
        )

        temp.write(result["text"].strip().encode())

    bar.progress(1.0, text="Transcriptions done!")
    bar.empty()

    with st.spinner("Processing text..."):
        from pipelines.indexing import get_indexing_pipeline

        pipe = get_indexing_pipeline(language)
        documents: dict = pipe.run(
            file_paths=[temp.name], meta={"book_id": book.id}
        )

    st.success(f"Book {book_title} successfully added")
