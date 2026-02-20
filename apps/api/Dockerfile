FROM python:3.11-slim

WORKDIR /app

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ctmsn /app/src/ctmsn
COPY apps/api/src/ctmsn_api /app/src/ctmsn_api

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "ctmsn_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
