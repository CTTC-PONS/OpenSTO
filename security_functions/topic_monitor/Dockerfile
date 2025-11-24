FROM python:3.11-slim

ENV PYTHONUNBUFFERED=0

RUN python3 -m pip install --upgrade 'pip==25.2'
RUN python3 -m pip install --upgrade 'setuptools==79.0.0' 'wheel==0.45.1'

WORKDIR /app
COPY _common /app/_common
RUN python3 -m pip install --no-cache-dir -r /app/_common/requirements.txt

COPY topic_monitor/requirements.txt /app/topic_monitor/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/topic_monitor/requirements.txt

COPY topic_monitor /app/topic_monitor

CMD ["python", "-m", "topic_monitor"]
