#!/bin/sh

sleep 5

celery -A project worker -l info -c 2