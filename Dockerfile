# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies and clean up temporary files
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    cmake \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for RabbitMQ (can be overridden)
ENV RABBITMQ_HOST=rabbitmq

# Expose the application port
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "./app.py"]
