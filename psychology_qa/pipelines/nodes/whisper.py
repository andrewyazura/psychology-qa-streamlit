from pathlib import Path

import librosa
from haystack.nodes.base import BaseComponent
from haystack.schema import Document
from transformers import pipeline


class WhisperTranscriber(BaseComponent):
    outgoing_edges = 1

    def __init__(self, model_name: str, language: str) -> None:
        self.pipe = pipeline(
            task="automatic-speech-recognition",
            model=model_name,
            chunk_length_s=30,
            device_map="auto",
        )

        self.generate_kwargs = {
            "task": "transcribe",
            "language": f"<|{language}|>",
        }

    def run(
        self, file_paths: list[Path], meta: dict | None = None
    ) -> tuple[dict, str]:
        documents = []

        for path in file_paths:
            audio, _ = librosa.load(path, sr=16_000)
            result = self.pipe(audio, generate_kwargs=self.generate_kwargs)

            documents.append(
                Document(content=result["text"].strip(), meta=meta)
            )

        return {"documents": documents}, "output_1"

    def run_batch(
        self, file_paths: list[Path], meta: dict | None = None
    ) -> tuple[dict, str]:
        return self.run(file_paths=file_paths, meta=meta)
