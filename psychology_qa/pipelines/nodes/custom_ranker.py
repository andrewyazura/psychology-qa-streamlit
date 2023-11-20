from haystack.nodes.base import BaseComponent
from haystack.schema import Document


class CustomRanker(BaseComponent):
    outgoing_edges = 1

    def __init__(self) -> None:
        pass

    def run(self, documents: list[Document] | None = None) -> tuple[dict, str]:
        return {"documents": documents}, "output_1"

    def run_batch(
        self, documents: list[Document] | None = None
    ) -> tuple[dict, str]:
        return self.run(documents=documents)
