import tempfile
from typing import TYPE_CHECKING

import streamlit as st
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls
from constants import LANGUAGES
from pipelines.processing import get_processing_pipeline
from pipelines.translate import translate

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()

files_form = st.empty()

with files_form.form("files"):
    language = st.selectbox("Select book's language", LANGUAGES)

    file: "UploadedFile" = st.file_uploader(
        "Upload a book",
        type=["txt", "pdf", "md", "doc", "docx"],
    )

    files_submitted = st.form_submit_button("Upload", use_container_width=True)

if files_submitted:
    if file is None:
        st.error("File is required")
        st.stop()

    files_form.empty()
    pipe = get_processing_pipeline(language)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(file.read())

        with st.spinner("Processing text..."):
            documents = pipe.run(file_paths=[temp.name])["documents"]

    if language != "en":
        documents = translate(language, "en", documents)

    st.json(documents)
