# syntax=docker/dockerfile:1

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV PATH="/home/user/miniconda3/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install --no-install-recommends -y build-essential software-properties-common wget && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install --no-install-recommends -y python3.10 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b && \
    rm Miniconda3-latest-Linux-x86_64.sh

COPY conda.yaml .
RUN conda env create --file=conda.yaml

CMD ["conda", "run", "-n", "psychology_qa", "streamlit", "run", "psychology_qa/app.py"]

COPY psychology_qa psychology_qa
COPY .streamlit .streamlit
COPY auth_config.yaml .
