from typing import TYPE_CHECKING

import librosa
import streamlit as st
import torch
from authenticator import display_authentication_controls
from st_pages import add_page_title, show_pages_from_config

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

add_page_title()
show_pages_from_config()
display_authentication_controls()


MODELS = (
    "openai/whisper-tiny",
    "openai/whisper-base",
    "openai/whisper-small",
    "openai/whisper-medium",
    "openai/whisper-large",
    "openai/whisper-large-v2",
)

LANGUAGES = (
    "en",
    "fr",
    "ua",
    "ru",
)

SAMPLE_RATE = 16_000

device = "cuda:0" if torch.cuda.is_available() else "cpu"
files_form = st.empty()

with files_form.form("files"):
    model_name = st.selectbox("Select a whisper model", MODELS)
    language = st.selectbox("Select language of the audiobook", LANGUAGES)

    files: list["UploadedFile"] = st.file_uploader(
        "Upload an audiobook (multiple files allowed)",
        accept_multiple_files=True,
        type=["wav", "mp3", "m4a"],
    )

    files_submitted = st.form_submit_button("Upload", use_container_width=True)

if files_submitted:
    files_form.empty()
    transcriptions = {}

    with st.spinner("Loading requested model..."):
        from transformers import pipeline

        pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_name,
            chunk_length_s=30,
            device=device,
        )

    bar = st.progress(0.0, text="Transcribing files")

    for i, file in enumerate(reversed(files)):
        bar.progress(i / len(files), text=f"Transcribing `{file.name}`")

        y, _ = librosa.load(file, sr=SAMPLE_RATE)
        duration = len(y) * SAMPLE_RATE

        result = pipe(
            y,
            generate_kwargs={
                "task": "transcribe",
                "language": f"<|{language}|>",
            },
        )

        transcriptions[file.name] = result["text"].strip()

    bar.progress(1.0, text="Transcriptions done!")

    st.json(transcriptions)
