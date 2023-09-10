from typing import Any, Callable

import streamlit as st

from config import streamlit_cache


def cache_resource() -> Callable[[Callable], Any]:
    return st.cache_resource(**streamlit_cache)
