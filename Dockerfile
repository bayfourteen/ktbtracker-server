# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS build
WORKDIR /app

# system deps for wheels only in build stage
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc pkg-config && rm -rf /var/lib/apt/lists/*

# envs that improve build behavior
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# cache-friendly dependency layers
COPY pyproject.toml poetry.lock* ./
RUN ls -l
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip wheel setuptools && \
    pip wheel --no-deps --wheel-dir=/wheels "." || ls -l /wheels || true

FROM python:3.12-slim AS runtime
WORKDIR /app

# system deps for wheels only in build stage
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# create non-root user
RUN useradd -m -u 10001 -s /usr/sbin/nologin appuser

# install deps from prebuilt wheels
COPY --from=build /wheels /wheels
RUN ls /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# copy only what you need (thanks to .dockerignore)
COPY ./src .

USER appuser
EXPOSE 8000

#CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn_worker.UvicornWorker", "--bind", "0.0.0.0:8000"]
