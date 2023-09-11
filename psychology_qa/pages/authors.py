import streamlit as st
from peewee import prefetch

from models import Author, Book
from pages.base import BasePage


class AuthorsPage(BasePage):
    def _display(self) -> None:
        with st.spinner("Loading authors..."):
            authors = prefetch(
                Author.select().order_by(Author.id.desc()),
                Book.select().order_by(Book.id.desc()),
            )

        if not authors:
            st.subheader("No authors")
            st.stop()

        for author in authors:
            st.header(author.name)

            if not author.books:
                st.write("No books added yet")
                continue

            book_titles = [book.title for book in author.books]
            tabs = st.tabs(book_titles)

            for tab, title in zip(tabs, book_titles):
                with tab:
                    st.subheader(title)


AuthorsPage().display()
