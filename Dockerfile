FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir python-telegram-bot==21.0

# Create data directory
RUN mkdir -p data

# Make sure the data directory has proper permissions
RUN chmod 755 data

EXPOSE 8080

CMD ["python", "main.py"]