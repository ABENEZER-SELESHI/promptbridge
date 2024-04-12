FROM python:3.11.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY config.conf.example ./config.conf.example

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["promptbridge", "--host", "0.0.0.0", "--port", "8080"]
