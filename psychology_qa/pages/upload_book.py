import tempfile
from typing import TYPE_CHECKING

import streamlit as st
from authenticator import display_authentication_controls
from pipelines.indexing import get_indexing_pipeline
from st_pages import add_page_title, show_pages_from_config

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()


LANGUAGES = ("en", "ru")

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
    pipeline = get_indexing_pipeline(language)

    with tempfile.NamedTemporaryFile() as fp:
        fp.write(file.read())
        fp.seek(0)

        result = pipeline.run(file_paths=[fp.name])

    st.json(result)
