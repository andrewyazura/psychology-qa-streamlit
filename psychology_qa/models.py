from peewee import (
    CharField,
    DatabaseProxy,
    FixedCharField,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
)
from pgvector.peewee import VectorField
from playhouse.postgres_ext import BinaryJSONField

database_proxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Author(BaseModel):
    name = CharField(max_length=255, unique=True)

    @classmethod
    def select_box_options(cls) -> dict[str, int]:
        return {author.name: author.id for author in cls.select()}


class Book(BaseModel):
    title = CharField(max_length=255, unique=True)
    author = ForeignKeyField(model=Author, backref="books")
    language = FixedCharField(max_length=2)

    def deep_delete(self) -> None:
        MetaDocument.delete().where(MetaDocument.book == self).execute()
        self.delete_instance()


class EmbeddingDocument(BaseModel):
    id = CharField(primary_key=True, max_length=32)
    embedding = VectorField(dimensions=768)


class MetaDocument(BaseModel):
    id = CharField(primary_key=True, max_length=32)
    split_id = IntegerField()

    content = TextField()
    meta = BinaryJSONField()

    embedding_document = ForeignKeyField(
        model=EmbeddingDocument,
        backref="meta_document",
        unique=True,
        on_delete="CASCADE",
    )
    book = ForeignKeyField(model=Book, backref="documents")
