# syntax=docker/dockerfile:1

FROM ubuntu:22.04 AS xpdf

RUN apt update && \
    apt install wget -y && \
    wget https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz && \
    tar -xvf xpdf-tools-linux-4.04.tar.gz && \
    cp xpdf-tools-linux-4.04/bin64/pdftotext . && \
    rm -rf xpdf-tools-linux-*

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt update && \
    apt install --no-install-recommends -y \
    build-essential software-properties-common wget && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y \
    python3.10 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 user

COPY --from=xpdf pdftotext /usr/local/bin

USER user
WORKDIR /home/user

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --requirement requirements.txt

CMD ["python3", "-m", "streamlit", "run", "psychology_qa/app.py"]

COPY --chown=user .streamlit .streamlit
COPY --chown=user psychology_qa psychology_qa
