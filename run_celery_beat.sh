#!/bin/sh

sleep 5

celery -A project worker -B -l info