ARG PYTHON_IMAGE=python:3.12.15-slim

FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


ARG PYTHON_IMAGE=python:3.12.15-slim

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:${PATH}"

RUN groupadd --gid 10001 kotone \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin kotone

COPY --from=builder /opt/venv /opt/venv
COPY . /app

RUN mkdir -p /app/data && chown 10001:10001 /app/data

WORKDIR /app/data
USER 10001

CMD ["python", "/app/bot.py"]
