#!/bin/bash
set -e

# Wait for SPIRE server to be ready
echo "Waiting for SPIRE server to be ready..."
sleep 10

# Export the server's bundle to the shared trust bundle location
echo "Exporting server's bundle to shared trust bundle location..."
spire-server bundle show -socketPath /tmp/spire-server/private/api.sock > /opt/spire/conf/trust/bundle.crt

# Create a join token for the SPIRE agent
echo "Creating join token for SPIRE agent..."
TOKEN=$(spire-server token generate -spiffeID spiffe://example.org/agent -ttl 3600)
echo "Token: $TOKEN"

# Register the agent
echo "Registering agent..."
spire-server agent join -token $TOKEN -socketPath /tmp/spire-server/private/api.sock

# Register the LLM agent workload
echo "Registering LLM agent workload..."
spire-server entry create \
    -socketPath /tmp/spire-server/private/api.sock \
    -parentID spiffe://example.org/agent \
    -spiffeID spiffe://example.org/agent/llm-agent \
    -selector docker:label:app:llm-agent \
    -ttl 3600

# Register the User API service workload
echo "Registering User API service workload..."
spire-server entry create \
    -socketPath /tmp/spire-server/private/api.sock \
    -parentID spiffe://example.org/agent \
    -spiffeID spiffe://example.org/service/user-service \
    -selector docker:label:app:user-service \
    -ttl 3600

echo "SPIRE registration complete!"
