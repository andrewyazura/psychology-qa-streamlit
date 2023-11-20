import logging

from haystack.nodes.base import BaseComponent
from haystack.schema import Document

from database import init_database
from models import Author, Book, EmbeddingDocument, MetaDocument

logger = logging.getLogger(__name__)

MAX_DISTANCE = 4


class PgvectorStore(BaseComponent):
    outgoing_edges = 1
    index = None
    label_index = None
    similarity = "dot_product"

    def __init__(self, batch_size: int) -> None:
        self.batch_size = batch_size

    def run(self, documents: list["Document"]) -> tuple[dict, str]:
        self.write_documents(documents)
        return {"documents": documents}, "output_1"

    def run_batch(self, documents: list["Document"]) -> tuple[dict, str]:
        return self.run(documents)

    def write_documents(self, documents: list["Document"], **_) -> None:
        self.database = init_database()

        batches = len(documents) // self.batch_size + 1

        for i in range(0, len(documents), self.batch_size):
            embedding_batch = []
            meta_document_batch = []

            for document in documents[i : i + self.batch_size]:
                embedding_batch.append(
                    {"id": document.id, "embedding": document.embedding}
                )

                if "_source_content" in document.meta:
                    content = document.meta.pop("_source_content")
                else:
                    content = document.content

                meta_document_batch.append(
                    {
                        "id": document.id,
                        "embedding_document_id": document.id,
                        "book_id": document.meta.pop("book_id"),
                        "split_id": document.meta.pop("_split_id"),
                        "content": content,
                        "meta": document.meta,
                    }
                )

            with self.database.atomic():
                EmbeddingDocument.insert_many(
                    embedding_batch
                ).on_conflict_ignore().execute()

                MetaDocument.insert_many(
                    meta_document_batch
                ).on_conflict_ignore().execute()

            batch = i // self.batch_size + 1
            logger.info(f"Batch {batch}/{batches} inserted")

    def query_by_embedding(
        self, query_emb: list, top_k: int = 10, **_
    ) -> list["Document"]:
        self.database = init_database()

        meta_documents = (
            MetaDocument.select(MetaDocument, Book, Author)
            .join(Book)
            .join(Author)
            .switch(MetaDocument)
            .join(EmbeddingDocument)
            .order_by(EmbeddingDocument.embedding.max_inner_product(query_emb))
            .iterator()
        )

        results = []

        for meta_document in meta_documents:
            if len(results) == top_k:
                break

            data = Document(
                id=meta_document.id,
                content=meta_document.content,
                meta={
                    **meta_document.meta,
                    "split_id": meta_document.split_id,
                    "book": {
                        "id": meta_document.book.id,
                        "title": meta_document.book.title,
                    },
                    "author": {
                        "id": meta_document.book.author.id,
                        "name": meta_document.book.author.name,
                    },
                },
            )

            for result in results:
                if result.meta["book"]["id"] == data.meta["book"]["id"]:
                    difference = (
                        result.meta["split_id"] - data.meta["split_id"]
                    )

                    if abs(difference) <= MAX_DISTANCE:
                        break

            else:
                results.append(data)

        return results
