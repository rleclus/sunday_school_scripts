#!/usr/bin/env bash

set -e

echo "🔍 Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    echo "👉 Install it from https://brew.sh"
    exit 1
fi

echo "🍺 Homebrew found."

echo "🔍 Checking system dependencies..."

BREW_PACKAGES=(
    tesseract
    poppler
    pipenv
)

for pkg in "${BREW_PACKAGES[@]}"; do
    if brew list "$pkg" &>/dev/null; then
        echo "✅ $pkg already installed"
    else
        echo "⬇️ Installing $pkg..."
        brew install "$pkg"
    fi
done

echo "🐍 Setting up Python virtual environment with pipenv..."

# Ensure pipenv uses the desired python version if available
if command -v python3.10 &> /dev/null; then
    pipenv --python $(which python3.10)
else
    pipenv --python python3
fi

pipenv install

echo "✅ Setup complete."
echo
echo "👉 To run the script:"
echo "   pipenv run python script.py <pdf_path> <output_folder>"
