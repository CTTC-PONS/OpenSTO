FROM python:3.11-slim

ENV PYTHONUNBUFFERED=0

RUN apt-get update --yes --quiet --quiet  && \
    apt-get install --yes --quiet --quiet --no-install-recommends build-essential libpcap0.8 libpcap0.8-dev && \
    apt-get clean --yes --quiet && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade 'pip==25.2'
RUN python3 -m pip install --upgrade 'setuptools==79.0.0' 'wheel==0.45.1'

WORKDIR /app
COPY _common /app/_common
RUN python3 -m pip install --no-cache-dir -r /app/_common/requirements.txt

COPY traffic_sniffer/requirements.txt /app/traffic_sniffer/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /app/traffic_sniffer/requirements.txt

COPY traffic_sniffer /app/traffic_sniffer

CMD ["python", "-m", "traffic_sniffer"]
