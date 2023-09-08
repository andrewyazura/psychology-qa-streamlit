from typing import TYPE_CHECKING

from haystack.nodes import TransformersTranslator
from haystack.nodes.base import BaseComponent

if TYPE_CHECKING:
    from haystack.schema import Document


class CustomIterativeTranslator(BaseComponent):
    outgoing_edges = 1

    def __init__(self, from_language: str, to_language: str) -> None:
        self.translator = TransformersTranslator(
            model_name_or_path=f"Helsinki-NLP/opus-mt-{from_language}-{to_language}"
        )

    def run(self, documents: list["Document"]) -> tuple[dict, str]:
        return {"documents": self.translate(documents)}, "output_1"

    def run_batch(self, documents: list["Document"]) -> tuple[dict, str]:
        return self.run(documents)

    def translate(self, documents: list["Document"]) -> list["Document"]:
        for document in documents:
            document.content = self.translator.translate(
                documents=[document],
            )[0].content

        return documents
