import time
from dataclasses import dataclass
from typing import Any

import streamlit as st

from config import prefixes
from models import MetaDocument
from views.base import BaseView


@dataclass
class Answer:
    role: str
    content: str
    meta: dict | None = None
    id: str | None = None

    @property
    def book_title(self) -> str:
        return self.meta["book"]["title"]

    @property
    def author_name(self) -> str:
        return self.meta["author"]["name"]


class ChatView(BaseView):
    view_title = "Psychology Q&A"
    view_icon = "🧠"

    def _display(self) -> None:
        if "answers" not in st.session_state:
            st.session_state.answers: list[Answer] = []

        for answer in st.session_state.answers:
            self._display_answer(answer)

        query = st.chat_input("Ask a psychology-related question")

        if not query:
            return

        new_answers = [Answer(role="user", content=query)]
        self._display_answer(new_answers[0])

        with st.spinner("Searching for answers..."):
            result = self._query_data(run_kwargs={"query": query})

        if not result["documents"]:
            new_answers.append(
                Answer(role="assistant", content="Nothing found...")
            )

        for document in result["documents"]:
            content = document.content.lstrip(prefixes["passage"])
            answer = Answer(
                role="assistant",
                content=content,
                meta=document.meta,
                id=document.id,
            )

            new_answers.append(answer)
            self._display_answer(answer)

        st.session_state.answers.extend(new_answers)

    def _query_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        import torch

        from pipelines.querying import get_querying_pipeline

        pipeline = get_querying_pipeline(**(init_kwargs or {}))
        result = pipeline.run(**(run_kwargs or {}))

        torch.cuda.empty_cache()
        return result

    def _display_answer(self, answer: Answer) -> None:
        with st.chat_message(answer.role):
            st.write(answer.content)

            if not answer.id:
                return

            meta_col, actions_col = st.columns(2)

            with meta_col:
                st.caption(f"from _{answer.book_title}_")
                st.caption(f"by _{answer.author_name}_")

            with actions_col:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.button(
                        "👍",
                        key=f"like-{answer.id}-{time.time()}",
                        on_click=self._like_answer,
                        args=(answer.id,),
                    )

                with col2:
                    st.button(
                        "👎",
                        key=f"dislike-{answer.id}-{time.time()}",
                        on_click=self._dislike_answer,
                        args=(answer.id,),
                    )

                with col3:
                    st.button(
                        "🗑",
                        key=f"delete-{answer.id}-{time.time()}",
                        on_click=self._delete_answer,
                        args=(answer.id,),
                    )

    def _like_answer(self, meta_document_id: str) -> None:
        st.toast("Not implemented yet", icon="🙅")

    def _dislike_answer(self, meta_document_id: str) -> None:
        st.toast("Not implemented yet", icon="🙅")

    def _delete_answer(self, meta_document_id: str) -> None:
        st.session_state.answers = [
            answer
            for answer in st.session_state.answers
            if answer.id is None or answer.id != meta_document_id
        ]

        with self.database.transaction():
            MetaDocument.delete().where(
                MetaDocument.id == meta_document_id
            ).execute()

        st.toast("Document deleted", icon="🗑")
