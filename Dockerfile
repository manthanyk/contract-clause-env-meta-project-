FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app"

RUN python -c "import uvicorn; print('uvicorn OK')" || echo "UVICORN NOT FOUND"

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]