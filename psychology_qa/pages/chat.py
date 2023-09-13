from typing import Any

import streamlit as st

from pages.base import BasePage


class ChatPage(BasePage):
    page_title = "Psychology Q&A"
    page_icon = ":brain:"

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

        result = self._query_data(
            run_kwargs={
                "query": query,
                "params": {"Retriever": {"top_k": 10}, "Ranker": {"top_k": 3}},
            }
        )

        if not result["documents"]:
            messages.append(
                {"role": "assistant", "content": "Nothing found..."}
            )

        for document in result["documents"]:
            messages.append({"role": "assistant", "content": document.content})

        for message in messages[1:]:
            self._display_message(message)

        st.session_state.messages.extend(messages)

    def _display_messages(self, messages: list[dict[str, str]]) -> None:
        for message in messages:
            self._display_message(message)

    def _display_message(self, message: dict[str, str]) -> None:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def _query_data(
        self, init_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> dict[str, Any]:
        with st.spinner("Searching for answers..."):
            from pipelines.querying import get_querying_pipeline

            pipeline = get_querying_pipeline(**(init_kwargs or {}))
            return pipeline.run(**(run_kwargs or {}))
