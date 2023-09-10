from peewee import (
    CharField,
    DatabaseProxy,
    ForeignKeyField,
    IntegerField,
    Model,
    TextField,
    UUIDField,
)
from pgvector.peewee import VectorField
from playhouse.postgres_ext import BinaryJSONField

database_proxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Author(BaseModel):
    name = CharField()


class Book(BaseModel):
    title = CharField()
    author = ForeignKeyField(
        model=Author,
        backref="books",
    )


class EmbeddingDocument(BaseModel):
    id = UUIDField(primary_key=True)
    embedding = VectorField(dimensions=768)


class MetaDocument(BaseModel):
    id = UUIDField(primary_key=True)
    split_id = IntegerField()

    content = TextField()
    meta = BinaryJSONField()

    embedding_document = ForeignKeyField(
        model=EmbeddingDocument,
        backref="meta_document",
        unique=True,
    )
    book = ForeignKeyField(
        model=Book,
        backref="documents",
    )
