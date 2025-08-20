FROM public.ecr.aws/docker/library/python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ml/code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN chmod +x app/serve.sh

# Make sure Python can import "app.*"
ENV PYTHONPATH=/opt/ml/code
# SageMaker requires the server on port 8080 with /ping and /invocations
# ENV PORT=8080

# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8080", "app.app:app"]
# IMPORTANT: SageMaker will pass "serve" — this wrapper handles it
ENTRYPOINT ["/opt/ml/code/app/serve.sh"]