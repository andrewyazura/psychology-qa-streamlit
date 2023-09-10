from typing import TYPE_CHECKING

from haystack.nodes import TransformersTranslator
from haystack.nodes.base import BaseComponent

if TYPE_CHECKING:
    from haystack.schema import Document


class CustomBatchTranslator(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self, from_language: str, to_language: str, batch_size: int = 10
    ) -> None:
        self.translator = TransformersTranslator(
            model_name_or_path=f"Helsinki-NLP/opus-mt-{from_language}-{to_language}"
        )
        self.batch_size = batch_size

    def run(self, documents: list["Document"]) -> tuple[dict, str]:
        return {"documents": self.translate(documents)}, "output_1"

    def run_batch(self, documents: list["Document"]) -> tuple[dict, str]:
        return self.run(documents)

    def translate(self, documents: list["Document"]) -> list["Document"]:
        translated_documents: list["Document"] = []

        for i in range(0, len(documents), self.batch_size):
            translated_documents.extend(
                self.translator.translate(
                    documents=documents[i : i + self.batch_size]
                )
            )

        for translated_document, document in zip(
            translated_documents, documents
        ):
            translated_document.meta["_source_content"] = document.content

        return translated_documents
