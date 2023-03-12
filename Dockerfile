FROM python:3.11 as venv

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Set up env
RUN python -m venv --copies env

# Install dependencies
COPY requirements.txt .
RUN /app/env/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy dependencies from builder
COPY --from=venv /app/env ./env

# Copy code
ADD publisher .

ENTRYPOINT [ "/app/env/bin/python", "nt2mqtt.py" ]