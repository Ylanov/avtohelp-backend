FROM python:3.7.2

RUN apt-get update -y
RUN apt-get -y install libcurl4-openssl-dev \
    libssl-dev \
    binutils \
    libproj-dev \
    gettext \
    gdal-bin

RUN apt-get clean autoclean
RUN apt-get autoremove --yes
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/


RUN pip install --upgrade pip
RUN pip install poetry
COPY Makefile /app/
COPY poetry.lock pyproject.toml /app/

RUN cd app/ && poetry config virtualenvs.create false \
  && poetry install --no-dev

COPY src /app/src/

WORKDIR /app

RUN mkdir media
RUN mkdir static

