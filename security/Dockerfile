FROM ubuntu:22.04

WORKDIR /usr/security/app

RUN apt update && apt upgrade -y
RUN apt install netcat curl wget python3.10 python3-pip git libmagic-dev libpq-dev -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 20

# Install Poetry
RUN pip install -U pip setuptools && pip install poetry && poetry config virtualenvs.create false

# Install osmclient
RUN git clone https://osm.etsi.org/gerrit/osm/osmclient /usr/osmclient
RUN cd /usr/osmclient && pip install -e . -r requirements.txt -r requirements-dev.txt
ENV PATH=${PATH}:/root/.local/bin

COPY ./pyproject.toml .

RUN poetry install --no-root

ENV PYTHONPATH=/usr/security/app

COPY ./src ./src
COPY ./scripts ./scripts
COPY ./alembic.ini .

CMD ["sh", "./scripts/start.sh"]
