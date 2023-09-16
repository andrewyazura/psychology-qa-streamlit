import logging
from typing import TYPE_CHECKING

import torch
from haystack.nodes import TransformersTranslator
from haystack.nodes.base import BaseComponent
from langdetect import detect

if TYPE_CHECKING:
    from haystack.schema import Document

logger = logging.getLogger(__name__)


class CustomBatchTranslator(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self, from_language: str, to_language: str, batch_size: int
    ) -> None:
        self.batch_size = batch_size
        self.from_language = from_language
        self.to_language = to_language

    def init_model(self, from_language: str) -> None:
        model_name = f"Helsinki-NLP/opus-mt-{from_language}-{self.to_language}"
        self.translator = TransformersTranslator(model_name_or_path=model_name)

        logger.info(f"Init translator using model {model_name}")

    def run(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        if self.from_language == "detect":
            detected_language = detect(query or documents[0].content)
            logger.info(f"Detected language: {detected_language}")

            if detected_language == self.to_language:
                return {"documents": documents}, "output_1"

            self.from_language = detected_language

        self.init_model(self.from_language)
        output = {}

        if query:
            output = {"query": self.translator.translate(query=query)}

        elif documents:
            output = {"documents": self.translate(documents)}

        del self.translator
        logger.debug("Freed VRAM")

        return output, "output_1"

    def run_batch(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        return self.run(query=query, documents=documents)

    def translate(self, documents: list["Document"]) -> list["Document"]:
        translated_documents: list["Document"] = []
        batches = len(documents) // self.batch_size + 1

        for i in range(0, len(documents), self.batch_size):
            translated_documents.extend(
                self.translator.translate(
                    documents=documents[i : i + self.batch_size]
                )
            )

            batch = i // self.batch_size + 1
            logger.info(f"Batch {batch}/{batches} translated")
            torch.cuda.empty_cache()

        for translated_document, document in zip(
            translated_documents, documents
        ):
            translated_document.meta["_source_content"] = document.content

        return translated_documents
