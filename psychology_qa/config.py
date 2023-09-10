from environs import Env

env = Env()

with env.prefixed("POSTGRES_"):
    postgres = {
        "database": env.str("DB"),
        "user": env.str("USER"),
        "password": env.str("PASSWORD"),
        "host": env.str("HOST"),
        "port": env.int("PORT"),
    }

    store_batch_size = env.int("STORE_BATCH_SIZE")

with env.prefixed("TRANSLATOR_"):
    translator = {
        "enabled": env.bool("ENABLED"),
        "base_language": env.str("BASE_LANGUAGE"),
        "batch_size": env.str("BATCH_SIZE"),
    }

embedding_model = env.str("EMBEDDING_MODEL")
ranker_model = env.str("RANKER_MODEL")

with env.prefixed("STREAMLIT_CACHE_"):
    streamlit_cache = {
        "ttl": env.int("TTL"),
        "max_entries": env.int("MAX_ENTRIES"),
        "show_spinner": env.bool("SHOW_SPINNER"),
    }
