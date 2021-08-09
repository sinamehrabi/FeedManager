#!/bin/bash

until nc -z rabbit 5672; do
    echo "$(date) - waiting for rabbitmq..."
    sleep 4
done

alembic revision --autogenerate -m "Added feed tables"

alembic upgrade head
pytest
nameko run --config config.yaml main