FROM registry.gitlab.com/agencypro/roadhelpbackend:python-3.7.2-based

COPY Makefile /app/

COPY src /app/src/

WORKDIR /app

RUN mkdir media
RUN mkdir static

