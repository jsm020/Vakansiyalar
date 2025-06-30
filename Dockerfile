# Dockerfile for Django + DRF + SimpleJWT
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
