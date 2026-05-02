FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies and Azure CLI via official script
RUN apt-get update && apt-get install -y     curl ca-certificates     && curl -sL https://aka.ms/InstallAzureCLIDeb | bash     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create temp directory for templates
RUN mkdir -p /tmp

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "app:app"]
