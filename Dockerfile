# HIBP Checker - Docker Image
#
# ⚡ Powered by Have I Been Pwned (https://haveibeenpwned.com) by Troy Hunt
#    Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
#
# This Docker image provides cross-platform support for Windows and macOS users

FROM python:3.11-slim

# Metadata
LABEL org.opencontainers.image.title="HIBP Checker"
LABEL org.opencontainers.image.description="Have I Been Pwned breach checker with comprehensive analysis"
LABEL org.opencontainers.image.authors="Bosco <gjbr@pm.me>"
LABEL org.opencontainers.image.source="https://github.com/greogory/hibp-checker"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.documentation="https://github.com/greogory/hibp-checker/blob/main/README.md"
LABEL org.opencontainers.image.version="2.3.3"

# Install bash and other required tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create app directory
WORKDIR /app

# Copy application files
COPY hibp_comprehensive_checker.py .
COPY hibp_workflow.sh .
COPY quick_start.sh .
COPY hibp_config.conf.example hibp_config.conf.example
COPY my_emails_template.txt my_emails_template.txt

# Copy dashboard files
COPY dashboard/ ./dashboard/

# Make scripts executable
RUN chmod +x hibp_workflow.sh quick_start.sh hibp_comprehensive_checker.py dashboard/start-dashboard.sh dashboard/start-dashboard-macos.sh

# Create directories for reports and logs
RUN mkdir -p /app/reports /app/logs /app/data

# Create a non-root user
RUN useradd -m -u 1000 hibpuser && \
    chown -R hibpuser:hibpuser /app

USER hibpuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app:${PATH}"
ENV HIBP_DATA_DIR=/app

# Healthcheck for dashboard service
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Default command shows help
CMD ["python3", "hibp_comprehensive_checker.py", "--help"]
