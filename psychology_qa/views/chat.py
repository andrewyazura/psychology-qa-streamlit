from typing import Any

import streamlit as st

from views.base import BaseView


class ChatView(BaseView):
    view_title = "Psychology Q&A"
    view_icon = "🧠"

    def _display(self) -> None:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            self._display_message(message)

        query = st.chat_input("Ask a psychology-related question")

        if not query:
            st.stop()

        messages = [{"role": "user", "content": query}]
        self._display_message(messages[0])

        with st.spinner("Searching for answers..."):
            result = self._query_data(run_kwargs={"query": query})

        if not result["documents"]:
            messages.append(
                {"role": "assistant", "content": "Nothing found..."}
            )

        for document in result["documents"]:
            messages.append(
                {
                    "role": "assistant",
                    "content": document.content,
                    "meta": document.meta,
                }
            )

        for message in messages[1:]:
            self._display_message(message)

        st.session_state.messages.extend(messages)

    def _display_messages(self, messages: list[dict[str, str]]) -> None:
        for message in messages:
            self._display_message(message)

    def _display_message(self, message: dict[str, str]) -> None:
        with st.chat_message(message["role"]):
            st.write(message["content"])

            meta = message.get("meta", {})

            if book := meta.get("book_title"):
                st.caption(f"from {book}")

            if author := meta.get("author_name"):
                st.caption(f"by {author}")

    def _query_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        from pipelines.querying import get_querying_pipeline

        pipeline = get_querying_pipeline(**(init_kwargs or {}))
        return pipeline.run(**(run_kwargs or {}))
