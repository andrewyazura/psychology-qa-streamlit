import logging
from pathlib import Path

import librosa
import torch
from haystack.nodes.base import BaseComponent
from haystack.schema import Document
from transformers import pipeline

logger = logging.getLogger(__name__)


class WhisperTranscriber(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self, model_name: str, language: str, batch_size: int | None = None
    ) -> None:
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_name,
            batch_size=batch_size,
            chunk_length_s=30,
            device_map="auto",
        )

        self.generate_kwargs = {
            "task": "transcribe",
            "language": f"<|{language}|>",
        }

        logger.info(f"Init transcriber using model {model_name}")

    def run(
        self, file_paths: list[Path], meta: dict | None = None
    ) -> tuple[dict, str]:
        documents = []

        for i, path in enumerate(file_paths, start=1):
            audio, _ = librosa.load(path, sr=16_000)
            result = self.pipe(audio, generate_kwargs=self.generate_kwargs)

            documents.append(
                Document(content=result["text"].strip(), meta=meta)
            )
            logger.info(f"Audio file {i}/{len(file_paths)} transcribed")
            torch.cuda.empty_cache()

        del self.pipe
        logger.debug("Freed VRAM")

        return {"documents": documents}, "output_1"

    def run_batch(
        self, file_paths: list[Path], meta: dict | None = None
    ) -> tuple[dict, str]:
        return self.run(file_paths=file_paths, meta=meta)
