import streamlit as st
from peewee import PeeweeException, prefetch
from st_pages import add_page_title, show_pages_from_config

from authenticator import display_authentication_controls
from database import init_database
from models import Author, Book

add_page_title()
show_pages_from_config()
display_authentication_controls()
init_database()

with st.form("author_form", clear_on_submit=True):
    st.subheader("Add author")

    name = st.text_input("Name")
    add_author = st.form_submit_button("Add")

    if add_author:
        try:
            Author.create(name=name)
            st.success("Author added")

        except PeeweeException:
            st.error("Failed to add author")

with st.spinner("Loading authors..."):
    authors = [
        {
            "Name": author.name,
            "Books": (
                ", ".join(book.title for book in author.books) or "No books"
            ),
        }
        for author in prefetch(Author.select(), Book.select())
    ]

if not authors:
    st.subheader("No authors")
    st.stop()

st.subheader("Authors")
st.dataframe(authors, hide_index=True, use_container_width=True)
