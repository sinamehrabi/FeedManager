#!/bin/bash

until nc -z rabbit 5672; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 1
done

alembic revision --autogenerate -m "Added feed tables"

alembic upgrade head

nameko run --config config.yaml main