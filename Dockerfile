FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    git \
    make \
    curl \
    unar \
    fontforge \
    python3-fontforge \
    python3-pip

RUN pip3 install \
    dataclasses-json \
    ipykernel \
    matplotlib