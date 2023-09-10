import streamlit as st
from peewee import PeeweeException, prefetch
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls
from database import init_database
from models import Author, Book

display_authentication_controls()
show_pages_from_config()
add_page_title()
init_database()

with st.spinner("Loading authors..."):
    authors = prefetch(
        Author.select().order_by(Author.id.desc()),
        Book.select().order_by(Book.id.desc()),
    )

AUTHORS_NAME_TO_ID = {author.name: author.id for author in authors}


col1, col2 = st.columns(2)

with col1:
    with st.form("author_form", clear_on_submit=True):
        st.subheader("Add an author")
        name = st.text_input("Name")

        if st.form_submit_button("Add", use_container_width=True):
            try:
                _ = Author.create(name=name)
                st.success("Author added")

            except PeeweeException:
                st.error(f"Failed to add {name}")

with col2:
    with st.form("book_form", clear_on_submit=True):
        st.subheader("Add a book")

        author_name = st.selectbox(
            "Select an author", AUTHORS_NAME_TO_ID.keys()
        )
        title = st.text_input("Title")

        if st.form_submit_button("Add", use_container_width=True):
            try:
                _ = Book.create(
                    title=title, author_id=AUTHORS_NAME_TO_ID[author_name]
                )

            except PeeweeException:
                st.error(f"Failed to add {title}")

if not authors:
    st.subheader("No authors")

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
