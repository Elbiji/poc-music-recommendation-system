# Setting python base image
FROM python:3.12-slim

# Python runtime settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Passing env from dockerfile to docker container
ARG FOO=${FOO}

ENV FOO=${FOO}

# Setup working directory inside container
WORKDIR /usr/src/app

# Install uv package manager
RUN pip install uv

# Utilizes docker to maximize cache hits
COPY pyproject.toml uv.lock ./

# Synchronize files
RUN uv sync

# Copy all local files to workdir
COPY . .

# Expose container to listen on port 5000
EXPOSE 5000

# Run when container is created
CMD [ "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000" ]
