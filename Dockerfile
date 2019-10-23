FROM python:3.7.2
ENV PYTHONUNBUFFERED 1
RUN apt-get update ; apt-get --assume-yes install binutils libproj-dev gdal-bin

RUN mkdir /code
WORKDIR /code
ADD requirements/base.txt /code/
ADD requirements/development.txt /code/
RUN pip install -r base.txt
RUN pip install -r development.txt
ADD . /code/
# ad gettext for makemessages command
RUN apt-get update && apt-get install -y gettext