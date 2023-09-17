import re
from typing import TYPE_CHECKING

from haystack.nodes import PreProcessor
from haystack.nodes.base import BaseComponent

if TYPE_CHECKING:
    from haystack.schema import Document


class CustomPreProcessor(BaseComponent):
    outgoing_edges = 1

    def __init__(
        self,
        prefix: str = "",
        language: str | None = None,
        split_by: str | None = None,
        split_length: int | None = None,
        split_overlap: int | None = None,
        respect_sentence: bool | None = None,
    ) -> None:
        self.prefix = prefix
        self.preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=True,
            language=language,
            split_by=split_by,
            split_length=split_length,
            split_overlap=split_overlap,
            split_respect_sentence_boundary=respect_sentence,
        )

    def run(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        if query:
            return {"query": self.process(query=query)}, "output_1"

        elif documents:
            return {"documents": self.process(documents=documents)}, "output_1"

        raise ValueError("At least one of the arguments must be provided")

    def run_batch(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> tuple[dict, str]:
        return self.run(query=query, documents=documents)

    def process(
        self,
        query: str | None = None,
        documents: list["Document"] | None = None,
    ) -> str | list["Document"]:
        if query:
            clean_query = self._replace_chars(query)
            return self.prefix + clean_query

        processed = self.preprocessor.process(documents)

        for document in processed:
            clean_text = self._replace_chars(document.content)
            document.content = self.prefix + clean_text

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
