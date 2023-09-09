from typing import TYPE_CHECKING

import streamlit as st
from transformers import pipeline

if TYPE_CHECKING:
    from transformers import Pipeline


@st.cache_resource(show_spinner=False)
def get_whisper_pipeline(model_name: str) -> Pipeline:
    return pipeline(
        task="automatic-speech-recognition",
        model=model_name,
        device_map="auto",
        chunk_length_s=30,
    )
