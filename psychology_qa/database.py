from typing import TYPE_CHECKING

from playhouse.postgres_ext import PostgresqlExtDatabase

from config import postgres
from models import Author, Book, EmbeddingDocument, MetaDocument
from utils import cache_resource

if TYPE_CHECKING:
    from peewee import DatabaseProxy


@cache_resource()
def init_database() -> "DatabaseProxy":
    from models import database_proxy

    database = get_database()
    database_proxy.initialize(database)
    database_proxy.create_tables(
        [Author, Book, EmbeddingDocument, MetaDocument]
    )

    return database_proxy


def get_database() -> PostgresqlExtDatabase:
    return PostgresqlExtDatabase(**postgres)
