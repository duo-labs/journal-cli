FROM python:3-slim

LABEL maintainer="labs@duo.com"

ARG hugoversion=0.57.2

RUN apt-get update && \
    apt-get install --no-install-recommends -y git wget ssh && \
    rm -rf /var/lib/apt/lists/*

# Install Hugo
WORKDIR /opt/hugo
COPY ./.docker/verify_hugo_checksum.sh .
RUN wget -q https://github.com/gohugoio/hugo/releases/download/v${hugoversion}/hugo_${hugoversion}_Linux-64bit.tar.gz && \
    wget -q https://github.com/gohugoio/hugo/releases/download/v${hugoversion}/hugo_${hugoversion}_checksums.txt && \
    ./verify_hugo_checksum.sh hugo_${hugoversion}_checksums.txt && \
    tar -C /usr/bin -xzf hugo_${hugoversion}_Linux-64bit.tar.gz hugo && \
    rm -rf /opt/hugo

# Setup the non privleged journal user
RUN groupadd -g 999 journal && \
    useradd -u 999 -m -g journal journal

RUN mkdir /journal && \
    chown journal:journal /journal && \
    mkdir /opt/journal-cli && \
    chown journal:journal /opt/journal-cli && \
    touch /.journal.toml && \
    chown journal:journal /.journal.toml

# Install Journal CLI dependencies
WORKDIR /opt/journal-cli
COPY requirements.txt .
RUN pip install -U -r requirements.txt

# Finally, set up and install Journal
USER journal
ENV JOURNAL_PATH=/journal
ENV JOURNAL_CONFIG=/.journal.toml
ENV JOURNAL_DOCKER=1
COPY . .
ENTRYPOINT [ "./journal" ]