from peewee import (
    CharField,
    DatabaseProxy,
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


class Book(BaseModel):
    title = CharField(max_length=255, unique=True)
    author = ForeignKeyField(model=Author, backref="books")


class EmbeddingDocument(BaseModel):
    id = CharField(primary_key=True, max_length=32)
    embedding = VectorField(dimensions=768)


class MetaDocument(BaseModel):
    id = CharField(primary_key=True, max_length=32)
    split_id = IntegerField()

    content = TextField()
    meta = BinaryJSONField()

    embedding_document = ForeignKeyField(
        model=EmbeddingDocument, backref="meta_document", unique=True
    )
    book = ForeignKeyField(model=Book, backref="documents")
