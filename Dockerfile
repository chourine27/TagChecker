FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "nfc_available_rest.app:app", "--host", "0.0.0.0", "--port", "6543"]
