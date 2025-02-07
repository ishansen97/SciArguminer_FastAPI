# Base image with CUDA support
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# Set environment variables for Python
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m ensurepip && python3 -m pip install --upgrade pip

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements.txt to install dependencies
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN python3 -m pip install -r requirements.txt

# Copy the rest of the project
COPY . /app

# Expose the port for the FastAPI application
EXPOSE 9000

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
