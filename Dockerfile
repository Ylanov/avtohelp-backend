FROM python:3.7.2
ENV PYTHONUNBUFFERED 1
RUN apt-get update

RUN apt-get --assume-yes install binutils libproj-dev gdal-bin gettext

RUN mkdir /code
WORKDIR /code
ADD requirements/base.txt /code/
ADD requirements/development.txt /code/
RUN pip install -r base.txt
RUN pip install -r development.txt
ADD . /code/

