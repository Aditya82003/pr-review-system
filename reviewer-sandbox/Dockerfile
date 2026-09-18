FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/liv/apt/lists/*

WORKDIR /app

COPY reviewer-sandbox/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY reviewer-sandbox/entrypoint.py .
COPY reviewer-sandbox/mcp_servers ./mcp_servers
COPY reviewer-sandbox/agent ./agent

RUN useradd --create-home reviewer
USER reviewer

ENTRYPOINT [ "python","entrypoint.py" ]
