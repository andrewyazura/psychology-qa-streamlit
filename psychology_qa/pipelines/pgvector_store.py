from haystack.nodes.base import BaseComponent
from haystack.schema import Document

from database import init_database
from models import Author, Book, EmbeddingDocument, MetaDocument


class PgvectorStore(BaseComponent):
    outgoing_edges = 1
    index = None
    label_index = None
    similarity = "dot_product"

    def __init__(self, batch_size: int) -> None:
        self.database = init_database()
        self.batch_size = batch_size

    def run(self, documents: list["Document"]) -> tuple[dict, str]:
        self.write_documents(documents)
        return {"documents": documents}, "output_1"

    def run_batch(self, documents: list["Document"]) -> tuple[dict, str]:
        return self.run(documents)

    def write_documents(self, documents: list["Document"], **_) -> None:
        for i in range(0, len(documents), self.batch_size):
            embedding_batch = []
            meta_document_batch = []

            for document in documents[i : i + self.batch_size]:
                embedding_batch.append(
                    {
                        "id": document.id,
                        "embedding": document.embedding,
                    }
                )

                meta_document_batch.append(
                    {
                        "id": document.id,
                        "embedding_document_id": document.id,
                        "book_id": document.meta.pop("book_id"),
                        "split_id": document.meta.pop("_split_id"),
                        "content": document.meta.pop("_source_content"),
                        "meta": document.meta,
                    }
                )

            with self.database.atomic():
                EmbeddingDocument.insert_many(embedding_batch).on_conflict(
                    conflict_target=(EmbeddingDocument.id,),
                    preserve=(EmbeddingDocument.embedding),
                ).execute()

                MetaDocument.insert_many(meta_document_batch).on_conflict(
                    conflict_target=(MetaDocument.id,),
                    preserve=(
                        MetaDocument.split_id,
                        MetaDocument.content,
                        MetaDocument.meta,
                    ),
                ).execute()

    def query_by_embedding(
        self, query_emb: list, top_k: int = 10, **_
    ) -> list["Document"]:
        meta_documents = (
            MetaDocument.select(
                MetaDocument.id,
                MetaDocument.content,
                MetaDocument.meta,
                EmbeddingDocument.embedding,
                Book.title.alias("book_title"),
                Author.name.alias("author_name"),
            )
            .join(Book)
            .join(Author)
            .switch(MetaDocument)
            .join(EmbeddingDocument)
            .order_by(
                EmbeddingDocument.embedding.max_inner_product(query_emb),
            )
            .limit(top_k)
        )

        return [
            Document(
                id=meta_document.id,
                embedding=meta_document.embedding_document.embedding,
                content=meta_document.content,
                meta={"db_document": meta_document},
            )
            for meta_document in meta_documents
        ]
