# syntax=docker/dockerfile:1

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

RUN apt update && \
    apt install --no-install-recommends -y \
    build-essential software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y \
    python3.10 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 user

USER user
WORKDIR /home/user

COPY psychology_qa psychology_qa
COPY .streamlit .streamlit
