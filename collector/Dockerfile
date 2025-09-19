FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Install cron
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/* && \
    echo "*/30 * * * * python3 collector.py >> /var/log/cron.log 2>&1" > /etc/cron.d/collector-cron && \
    chmod 0644 /etc/cron.d/collector-cron && \
    crontab /etc/cron.d/collector-cron && \
    touch /var/log/cron.log

# Run cron in foreground
CMD ["cron", "-f", "-L", "15"]
