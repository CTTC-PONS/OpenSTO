FROM python:3.11-slim

ENV PYTHONUNBUFFERED=0

RUN python3 -m pip install --upgrade 'pip==25.2'
RUN python3 -m pip install --upgrade 'setuptools==79.0.0' 'wheel==0.45.1'

WORKDIR /app
COPY _common /app/_common
RUN python3 -m pip install --no-cache-dir -r /app/_common/requirements.txt

COPY ai_inference/requirements.txt /app/ai_inference/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/ai_inference/requirements.txt

COPY ai_inference /app/ai_inference

CMD ["python", "-m", "ai_inference"]
