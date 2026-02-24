# Use the base Python 3.11 dev container
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install ffmpeg for PyDub
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU version) and dependencies
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Set the default workdir
WORKDIR /workspaces/kids-content-engine
