from environs import Env

env = Env()

env.read_env(".app.env")
env.read_env(".postgres.env")

# system

with env.prefixed("LOGGING_"):
    logging = {
        "level": env.log_level("LEVEL"),
        "format": env.str("FORMAT"),
        "date_format": env.str("DATE_FORMAT"),
    }

with env.prefixed("STREAMLIT_CACHE_"):
    streamlit_cache = {
        "ttl": env.int("TTL"),
        "max_entries": env.int("MAX_ENTRIES"),
        "show_spinner": env.bool("SHOW_SPINNER"),
    }

# database

with env.prefixed("POSTGRES_"):
    postgres = {
        "database": env.str("DB"),
        "user": env.str("USER"),
        "password": env.str("PASSWORD"),
        "host": env.str("HOST"),
        "port": env.int("PORT"),
    }

    store_batch_size = env.int("STORE_BATCH_SIZE", 10_000)

# pipeline

with env.prefixed("PREPROCESSOR_"):
    preprocessor = {
        "split_by": env.str("SPLIT_BY"),
        "split_length": env.int("SPLIT_LENGTH"),
        "split_overlap": env.int("SPLIT_OVERLAP"),
        "respect_sentence": env.bool("RESPECT_SENTENCE"),
    }

with env.prefixed("EMBEDDING_"):
    embedding = {
        "embedding_model": env.str("MODEL"),
        "model_format": env.str("FORMAT"),
        "top_k": env.int("TOP_K"),
    }

# optional

with env.prefixed("PREFIX_"):
    prefixes = {
        "query": env.str("QUERY", ""),
        "passage": env.str("PASSAGE", ""),
    }

with env.prefixed("TRANSLATOR_"):
    translator = {
        "enabled": env.bool("ENABLED", False),
        "base_language": env.str("BASE_LANGUAGE", "en"),
        "batch_size": env.int("BATCH_SIZE", 1),
    }

whisper_batch_size = env.int("WHISPER_BATCH_SIZE", 1)
