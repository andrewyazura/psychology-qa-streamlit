import tempfile
from typing import TYPE_CHECKING

import librosa as lr
import streamlit as st
from authenticator import display_authentication_controls
from constants import LANGUAGES, SAMPLE_RATE, WHISPER_MODELS
from st_pages import add_page_title, show_pages_from_config

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()

files_form = st.empty()

with files_form.form("files"):
    language = st.selectbox("Select language of the audiobook", LANGUAGES)
    model_name = st.selectbox("Select a whisper model", WHISPER_MODELS)

    files: list["UploadedFile"] = st.file_uploader(
        "Upload an audiobook (multiple files allowed)",
        accept_multiple_files=True,
        type=["wav", "mp3", "m4a"],
    )

    files_submitted = st.form_submit_button("Upload", use_container_width=True)

if not files_submitted:
    st.stop()

if not files:
    st.error("File is required")
    st.stop()

files_form.empty()

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
        from pipelines.processing import get_processing_pipeline

        pipe = get_processing_pipeline(language)
        documents = pipe.run(file_paths=[temp.name])

st.json(documents)
