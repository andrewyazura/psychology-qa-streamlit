import streamlit as st

from pages.base import BasePage


class AppPage(BasePage):
    def _display(self) -> None:
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        for message in st.session_state["messages"]:
            self.display_message(message)

        query = st.chat_input("Ask a psychology-related question")

        if not query:
            st.stop()

        messages = [{"role": "user", "content": query}]
        self.display_message(messages[0])

        result = self.query_data(
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
            self.display_message(message)

        st.session_state["messages"].extend(messages)

    def display_messages(self, messages: list[dict[str, str]]) -> None:
        for message in messages:
            self.display_message(message)

    def display_message(self, message: dict[str, str]) -> None:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


AppPage().display()
