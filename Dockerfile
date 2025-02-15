FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-root

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8123

# Command to run the application
CMD ["poetry", "run", "python", "server.py", "start-server"]