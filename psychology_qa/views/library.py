import streamlit as st
from peewee import JOIN, IntegrityError, fn, prefetch

from models import Author, Book, MetaDocument
from views.base import BasePage


class LibraryPage(BasePage):
    page_title = "Library"
    page_icon = "🗃️"

    def _display(self) -> None:
        self.add_author_form()
        self.list()

    def add_author_form(self) -> None:
        with st.form("author_form", clear_on_submit=True):
            st.subheader("Add an author")
            name = st.text_input("Name")

            if st.form_submit_button("Add", use_container_width=True):
                try:
                    _ = Author.create(name=name)
                    st.toast("Author added", icon="✍")

                except IntegrityError:
                    st.error(f"Author alredy exists: {name}")

    def list(self) -> None:
        with st.spinner("Loading authors..."):
            authors = prefetch(
                Author.select().order_by(Author.id.desc()),
                Book.select(
                    Book, fn.COUNT(MetaDocument.id).alias("documents_count")
                )
                .join(MetaDocument, JOIN.LEFT_OUTER)
                .group_by(Book.id)
                .order_by(Book.id.desc()),
            )

        if not authors:
            return

        st.header("Authors")

        for author in authors:
            st.subheader(author.name)
            st.button(
                "Delete author",
                key=f"delete-{author.id}",
                on_click=self.delete_author,
                args=(author,),
            )

            if not author.books:
                st.caption("No books added yet.")
                continue

            for book in author.books:
                with st.expander(book.title):
                    st.button(
                        "Delete book",
                        key=f"delete-book-{book.id}",
                        on_click=self.delete_book,
                        args=(book,),
                    )
                    st.write(f"Documents in DB: {book.documents_count}")

    def delete_author(self, author: Author) -> None:
        if author.books:
            st.error("You have to delete author's books first")
            return

        with self.database.transaction():
            author.delete_instance()

        st.toast(f"Author '{author.name}' deleted", icon="🗑️")

    def delete_book(self, book: Book) -> None:
        with self.database.transaction():
            book.deep_delete()

        st.toast(f"Book '{book.title}' deleted", icon="🗑️")
