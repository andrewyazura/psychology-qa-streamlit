import re

from haystack.nodes import PreProcessor
from haystack.nodes.base import BaseComponent
from haystack.schema import Document


class CustomPreProcessor(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self,
        split_by: str = "word",
        split_length: int = 500,
        split_overlap: int = 100,
        language: str = "en",
    ) -> None:
        self.preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=True,
            split_respect_sentence_boundary=True,
            progress_bar=False,
            split_by=split_by,
            split_length=split_length,
            split_overlap=split_overlap,
            language=language,
        )

    def run(self, documents: list[Document]) -> tuple[dict, str]:
        return {"documents": self.process(documents)}, "output_1"

    def run_batch(self, documents: list[Document]) -> tuple[dict, str]:
        return self.run(documents)

    def process(self, documents: list[Document]) -> list[Document]:
        processed = self.preprocessor.process(documents)

        for document in processed:
            document.content = self._replace_chars(document.content)

        return processed

    @staticmethod
    def _replace_chars(string: str) -> str:
        chars = {
            "\xa0 ": " ",
            "\xa0": " ",
            "\x0c": "",
            "-\n\n": "",
            "-\n": "",
            "\n\n": " ",
            "\n": " ",
        }

        for pattern, repl in chars.items():
            string = re.sub(pattern, repl, string)

        return string
