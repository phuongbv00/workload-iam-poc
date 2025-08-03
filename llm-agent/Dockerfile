FROM python:3.11-slim

WORKDIR /app

# Copy the requirements and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the agent code
COPY agent /app/agent

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=http://envoy-agent:9090

# Run the agent
CMD ["python", "-m", "agent.agent"]