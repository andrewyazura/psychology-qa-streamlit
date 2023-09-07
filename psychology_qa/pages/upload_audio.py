import tempfile
from typing import TYPE_CHECKING

import librosa
import streamlit as st
import torch
from st_pages import add_page_title, show_pages_from_config
from transformers import pipeline

from authenticator import display_authentication_controls
from pipelines.processing import get_processing_pipeline
from pipelines.translate import translate

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()

LANGUAGES = (
    "en",
    "ru",
)

MODELS = (
    "openai/whisper-tiny",
    "openai/whisper-base",
    "openai/whisper-small",
    "openai/whisper-medium",
    "openai/whisper-large",
    "openai/whisper-large-v2",
)

SAMPLE_RATE = 16_000

device = "cuda:0" if torch.cuda.is_available() else "cpu"
files_form = st.empty()

with files_form.form("files"):
    language = st.selectbox("Select language of the audiobook", LANGUAGES)
    model_name = st.selectbox("Select a whisper model", MODELS)

    files: list["UploadedFile"] = st.file_uploader(
        "Upload an audiobook (multiple files allowed)",
        accept_multiple_files=True,
        type=["wav", "mp3", "m4a"],
    )

    files_submitted = st.form_submit_button("Upload", use_container_width=True)

if files_submitted:
    if not files:
        st.error("File is required")
        st.stop()

    files_form.empty()

    with st.spinner("Loading requested model..."):
        pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_name,
            device=device,
            chunk_length_s=30,
        )

    bar = st.empty()
    bar.progress(0.0, text="Transcribing files")

    with tempfile.NamedTemporaryFile() as temp:
        for i, file in enumerate(reversed(files)):
            bar.progress(i / len(files), text=f"Transcribing {i}/{len(files)}")
            audio, _ = librosa.load(file, sr=SAMPLE_RATE)

            result = pipe(
                audio,
                generate_kwargs={
                    "task": "transcribe",
                    "language": f"<|{language}|>",
                },
            )

            temp.write(result["text"].strip().encode())

        bar.progress(1.0, text="Transcriptions done!")
        bar.empty()

        pipeline = get_processing_pipeline(language)
        documents = pipeline.run(file_paths=[temp.name])["documents"]

    if language != "en":
        documents = translate(language, "en", documents)

    st.json(documents)
