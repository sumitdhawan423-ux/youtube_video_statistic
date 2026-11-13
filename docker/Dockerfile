# Multi-stage Dockerfile for PySpark Big Data Analytics Client
FROM python:3.11-slim-bullseye

LABEL maintainer="Antigravity Big Data Team"
LABEL description="PySpark Client Container with Hadoop and Data Science Libraries"

# Install OpenJDK 11 and essential CLI tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    curl \
    procps \
    bash \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /workspace

# Install Python requirements
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888 4040

CMD ["bash"]

