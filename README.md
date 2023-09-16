---
title: Psychology Q&A
emoji: 🧠
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 8501
models:
    - intfloat/multilingual-e5-large
tags:
    - "Sentence similarity"
    - "Semantic search"
---

# Psychology Q&A

This project was built for the purpose of indexing a dataset of
psychology books and performing semantic search on them later.
However, it is not tailored for any specific field or data, so
you can easily use it for your personal needs.

You can upload `txt`, `pdf`, `md`, and `doc` files, but also
`mp3` audio, which will be transcribed by Whisper.

## Embedding models

This is a list of embedding models I've tried, along with my
feedback. I'd recommend using `intfloat/multilingual-e5-large`,
as it is both multilingual and supports asymmetric search.
More info on Sentence-BERT: [sbert.net](https://www.sbert.net/)

Ideally, you'd want to fine-tune the model to your data
to make the search more efficient.

| Name                                    | Embedding size | Languages    | Search type              | Link                                                                                                | Results                                                               |
| --------------------------------------- | -------------- | ------------ | ------------------------ | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `multilingual-e5-large`                 | 1024           | Multilingual | Symmetric and asymmetric | [huggingface 🤗](https://huggingface.co/intfloat/multilingual-e5-large)                              | ✅ Best of all, allows producing embeddings without translating text   |
| `multi-qa-mpnet-base-dot-v1`            | 768            | English-only | Asymetric                | [huggingface 🤗](https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-dot-v1)            | 👌 Good, but requires translation                                      |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384            | Multilingual | Symmetric                | [huggingface 🤗](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) | 👎 Only fits for symmetric search, but does not require translation    |
| `all-mpnet-base-v2`                     | 768            | English-only | Symmetric                | [huggingface 🤗](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)                     | 🚫 Bad, requires translation and is only suitable for symmetric search |

## Database setup

Add `pgvector` extension before creating tables:

```sql
CREATE EXTENSION vector;
```

## Screenshots

<img src="./assets/pages/chat.png" alt="Chat page with example answers" width=400> <img src="./assets/pages/library.png" alt="List of authors and book profiles" width=400> <img src="./assets/pages/upload.png" alt="Upload page for books" width=400> <img src="./assets/pages/upload_audio.png" alt="Upload page for audio" width=400>

## To Do

- [x] Authentication
- [ ] Gather feedback on answers to fine-tune model later
- [ ] Allow revealing more text after receiving answer
- [ ] Show source of answer on chat page
