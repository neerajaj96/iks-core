FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY data/ ./data/
COPY server/ ./server/
RUN pip install --no-cache-dir fastapi uvicorn && \
    python3 -c "from src.vada.graph import load_seed; print(load_seed().summary())"
EXPOSE 8000
CMD ["uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000"]
