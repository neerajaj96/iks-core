FROM python:3.14-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY iks_core/ ./iks_core/
COPY data/ ./data/
COPY server/ ./server/
RUN pip install --no-cache-dir fastapi uvicorn ./. && \
    python3 -c "import iks_core.vada.graph as g; print(g.load_seed().summary())"
EXPOSE 8000
CMD ["uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000"]
