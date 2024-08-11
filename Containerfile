# Use Python 3.11 as the base image
FROM python:3.10.14-slim-bullseye

# Set the working directory in the container
WORKDIR /app


# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Upgrade llama-cpp-python to the latest version
RUN pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir

RUN pip install "numpy<2"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variables
ENV PROFILE=production
ENV MODEL_PATH=/app/model/Phi-3.1-mini-4k-instruct-Q8_0.gguf

# Run main.py when the container launches
CMD ["python", "main.py"]