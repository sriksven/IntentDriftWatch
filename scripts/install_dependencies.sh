#!/bin/bash
set -e

# Print commands and exit on error
set -x

echo "Starting clean installation for macOS..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found"
    exit 1
fi

# Upgrade pip first
python3 -m pip install --upgrade pip

# Install PyTorch specifically for CPU/MPS (Mac) first to avoid pulling in CUDA
# We pin to stable versions compatible with sentence-transformers
echo "Installing macOS-optimized PyTorch..."
python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Install the rest of the requirements, avoiding cache to save space
echo "Installing remaining dependencies..."
python3 -m pip install -r requirements.txt --no-cache-dir

echo "Installation complete!"
