from typing import TYPE_CHECKING

from haystack.nodes import TransformersTranslator
from haystack.nodes.base import BaseComponent
from langdetect import detect

if TYPE_CHECKING:
    from haystack.schema import Document


class CustomBatchTranslator(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self, from_language: str, to_language: str, batch_size: int
    ) -> None:
        self.batch_size = batch_size
        self.to_language = to_language

        if from_language == "detect":
            self.translator = None
            return

        self.init_translator(from_language)

    def init_translator(self, from_language: str) -> None:
        self.translator = TransformersTranslator(
            model_name_or_path="Helsinki-NLP/opus-mt-"
            f"{from_language}-{self.to_language}"
        )

    def run(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        if not self.translator:
            detected_language = detect(query or documents[0].content)

            if detected_language == self.to_language:
                return {"documents": documents}, "output_1"

            self.init_translator(detected_language)

        if query:
            return {
                "query": self.translator.translate(query=query)
            }, "output_1"

        return {"documents": self.translate(documents)}, "output_1"

    def run_batch(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        return self.run(query=query, documents=documents)

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
