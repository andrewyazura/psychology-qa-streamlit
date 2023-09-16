# syntax=docker/dockerfile:1

FROM python:3.10-slim-bookworm AS requirements
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    python -m venv --copies --upgrade-deps /opt/venv && \
    pip install --requirement requirements.txt

FROM ubuntu:22.04 AS xpdf

RUN apt-get update && \
    apt-get install wget -y && \
    wget https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz && \
    tar -xvf xpdf-tools-linux-4.04.tar.gz && \
    cp xpdf-tools-linux-4.04/bin64/pdftotext . && \
    rm -rf xpdf-tools-linux-*

FROM nvidia/cuda:11.7.1-runtime-ubuntu22.04

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential software-properties-common libfontconfig && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install --no-install-recommends -y \
    python3.10 python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=xpdf pdftotext /usr/local/bin
COPY --from=requirements /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
RUN python -c "import nltk; nltk.download('punkt')"

CMD ["python", "-m", "streamlit", "run", "psychology_qa/app.py"]

COPY .streamlit .streamlit
COPY psychology_qa psychology_qa
