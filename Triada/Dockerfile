FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY Triada/orchestrator/requirements.txt ./requirements_orch.txt
COPY Triada/manager/requirements.txt ./requirements_mgr.txt
COPY Triada/worker/requirements.txt ./requirements_wrk.txt

RUN pip install --no-cache-dir -r requirements_orch.txt && \
    pip install --no-cache-dir -r requirements_mgr.txt && \
    pip install --no-cache-dir -r requirements_wrk.txt

COPY . .

# Set PYTHONPATH to repo root
ENV PYTHONPATH=/app

# Default command (overridden in render.yaml)
CMD ["python", "Triada/manager/main.py"]
