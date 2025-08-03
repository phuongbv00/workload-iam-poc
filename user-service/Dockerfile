FROM python:3.11-slim

WORKDIR /app

# Copy the requirements and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the application code
COPY api /app/api

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "-m", "api.main"]