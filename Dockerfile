FROM public.ecr.aws/docker/library/python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ml/code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# SageMaker requires the server on port 8080 with /ping and /invocations
ENV PORT=8080

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8080", "app.app:app"]
