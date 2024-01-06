FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/bin/python3.10 -m pip install --upgrade pip && \
    pip install -r requirements.txt 

RUN python3.10 -m spacy download fr_core_news_md && \
    python3.10 -m spacy download en_core_web_sm

CMD ["streamlit", "run", "home.py"]
