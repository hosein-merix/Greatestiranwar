#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p data

# Set proper permissions
chmod 755 data

# Start the bot
python main.py