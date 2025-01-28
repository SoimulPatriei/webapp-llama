#!/bin/bash

# Define RabbitMQ host and port
RABBITMQ_HOST="rabbitmq"
RABBITMQ_PORT="5672"

# Wait for RabbitMQ to be available
echo "Waiting for RabbitMQ to be available..."
while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
  sleep 1
done

echo "RabbitMQ is up. Starting the application..."
exec "$@"
