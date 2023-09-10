from typing import TYPE_CHECKING

from transformers import pipeline

from utils import cache_resource

if TYPE_CHECKING:
    from transformers import Pipeline


@cache_resource()
def get_whisper_pipeline(model_name: str) -> Pipeline:
    return pipeline(
        task="automatic-speech-recognition",
        model=model_name,
        device_map="auto",
        chunk_length_s=30,
    )
