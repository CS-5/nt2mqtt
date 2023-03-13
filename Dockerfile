FROM python:3.11-slim AS builder

RUN apt update && apt upgrade -y
RUN apt install build-essential -y

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python dependencies
COPY ./bridge/requirements.txt .
RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

FROM python:3.11-slim

# Update packages
RUN apt update && apt upgrade -y
RUN apt install libatomic1 -y

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app .
ENV PYTHONPATH="${PYTHONPATH}:/app/dependencies"

# Copy code
ADD bridge .

ENTRYPOINT [ "python", "bridge.py" ]