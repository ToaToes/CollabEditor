#!/bin/bash

cd "$(dirname "$0")"

echo "Starting server using venv Python..."
./venv/bin/python server.py

read
