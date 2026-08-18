# OpenShift Operator Upgrade Advisor - Docker Image
FROM python:3.11-slim

LABEL maintainer="your-team@company.com"
LABEL description="OpenShift Operator Upgrade Advisor"

# Set working directory
WORKDIR /app

# Copy application files
COPY backend/simple_server_enhanced.py /app/backend/
COPY compatibility_matrix.json /app/
COPY index.html /app/

# No dependencies needed - Python stdlib only!

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the server
WORKDIR /app/backend
CMD ["python3", "simple_server_enhanced.py"]
