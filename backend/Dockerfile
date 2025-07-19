FROM python:3.13.5-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /build/requirements.txt

COPY ./app /build/app
COPY ./schemas /build/schemas

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
