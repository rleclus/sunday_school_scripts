#!/bin/bash
echo "Setting up virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt || true
python balancing_scale.py