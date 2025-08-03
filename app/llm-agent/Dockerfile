FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH"

COPY ./pyproject.toml ./uv.lock /app/
RUN uv sync

COPY ./app/llm-agent/main.py /app/

ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=http://envoy-agent:9090

CMD ["python", "main.py"]
