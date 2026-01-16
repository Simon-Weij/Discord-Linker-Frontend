FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
COPY src/ ./src/
RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

CMD ["python", "-m", "discord_linker_frontend"]
