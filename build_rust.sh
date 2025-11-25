#!/bin/bash
# Build and install the Rust decoder extension

set -e  # Exit on error

echo "Building Rust extension with maturin..."
uv run maturin build

echo "Installing Rust extension..."
uv pip install -e . --reinstall

echo "Build and install complete!"

