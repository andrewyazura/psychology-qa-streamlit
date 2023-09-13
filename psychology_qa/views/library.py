import streamlit as st
from peewee import IntegrityError, prefetch

from models import Author, Book
from views.base import BasePage


class LibraryPage(BasePage):
    page_title = "Library"
    page_icon = ":card_file_box:"

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
                    st.success("Author added")

                except IntegrityError:
                    st.error(f"Author alredy exists: {name}")

    def list(self) -> None:
        with st.spinner("Loading authors..."):
            authors = prefetch(
                Author.select().order_by(Author.id.desc()),
                Book.select().order_by(Book.id.desc()),
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

    def delete_author(self, author: Author) -> None:
        if author.books:
            st.error("You have to delete author's books first")
            return

        author.delete_instance()

    def delete_book(self, book: Book) -> None:
        book.deep_delete()
