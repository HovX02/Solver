FROM python:3.12-slim

# Install system dependencies for browsers and Xvfb
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libasound2 \
    libglib2.0-0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    librandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fetch Camoufox browser binaries and install Playwright dependencies
RUN python3 -m camoufox fetch && \
    python3 -m playwright install-deps && \
    playwright install chromium

# Copy application files
COPY . .

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV HEADLESS=true

EXPOSE 8000

CMD ["python3", "api_server.py"]
