# Workload IAM Proof of Concept

This repository contains a proof of concept implementation of Workload Identity and Access Management (IAM) for a system where an LLM agent needs to access a REST API.

## Architecture

The architecture follows the principles outlined in the INSTRUCTION.md file:

1. **LLM Agent**: A Python application that simulates an LLM-based system making requests to a user management API.
2. **User Management API**: A FastAPI application that provides CRUD operations for user data.
3. **SPIFFE/SPIRE**: Provides workload identity management.
4. **Envoy Proxies**: Act as sidecars for both the agent and API, handling mTLS communication.
5. **Open Policy Agent (OPA)**: Enforces access control policies based on the workload identity.

![Architecture Diagram](https://mermaid.ink/img/pako:eNqFkk9PwzAMxb9KlBOgSf0HhMQBCYHEBSFx6A6mqTfSNHFkO2xF7bvjdmWMTdqpfn7Pz7Jz5JVRyHLpjfUNvGkHDVwZXTu0cAXPYLXTDRjwFVRQWQMVOFDWgYfKGvBqB9Zp8BqcbqBFZ6HVDdxBZTXUYMFBBRsIFVRGNWDhHpzRFVjdQgXvYJWDDXgVXqGCN_AKnNlCBc_gVQsOPLTKQQUPUDsVXqGCLVjVQg0OfFihhgqewDsHtYIKbsEpDxU8QqM9OKigVt6Dg1t4Uat_Tn_Bj-AcVPAClYcaKnhVvgUHFTTKe6jgGWrloIJnqJWHCp7AKw-1ggpuoFYeKngEpzxU8AiN9lDBHVTKQwWP4JWHCu7BKQ8VPIFXHiq4B6c8VPAIXnmo4B6c8lDBE3jloYJ7cMpDBY_glYcK7sEpDxU8glceKrgHpzxU8AheeTjyPOOZkKbkWc-zQRQiEVmWiVHMRZKKJBVJJpJhNBJpOhJxnIo4GYlkPBbJZCKS6XQkZrNUzOcTMV-MxXK5FKvVSqzXa7HZbMR2uxW73U7s93tx2B_E8XgUp9NJnM9ncblcxPV6Fbfb7Zv_AKNLzQo?type=png)

## Components

### LLM Agent
- Located in `agent/agent.py`
- Simulates an LLM-based system making API requests
- Uses a SPIFFE ID for authentication

### User Management API
- Located in `api/main.py`
- Provides CRUD operations for user data
- Logs request headers for debugging

### SPIFFE/SPIRE Configuration
- Server configuration: `spire/server/server.conf`
- Agent configuration: `spire/agent/agent.conf`
- Registration script: `spire/register_entries.sh`

### Envoy Proxy Configuration
- Agent-side configuration: `envoy/agent/envoy.yaml`
- Server-side configuration: `envoy/server/envoy.yaml`

### OPA Policy
- Configuration: `opa/config.yaml`
- Policy rules: `opa/policy.rego`

## Running the PoC

### Prerequisites
- K8s/Minikube

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/workload-iam-poc.git
   cd workload-iam-poc
   ```

2. Build and start the services:
   [Quickstart with K8s](./k8s)

3. The LLM agent will automatically run a demo that:
   - Creates users
   - Lists users
   - Gets a specific user
   - Updates a user
   - Deletes a user

4. You can observe the logs to see:
   - SPIRE registration process
   - OPA authorization decisions
   - API request/response flow
   - mTLS certificate exchange

## Security Features

1. **Workload Identity**:
   - Each workload has a unique SPIFFE ID
   - No static credentials or secrets
   - Identity based on workload attributes (Docker labels)

2. **Mutual TLS (mTLS)**:
   - All service-to-service communication is encrypted
   - Both client and server authenticate each other
   - Certificates are automatically rotated by SPIRE

3. **Policy-Based Access Control**:
   - Fine-grained access control based on:
     - Workload identity (SPIFFE ID)
     - HTTP method
     - Request path
   - Default deny policy
   - Centralized policy management with OPA

4. **Zero Trust Architecture**:
   - No implicit trust between services
   - Every request is authenticated and authorized
   - Network-level security with Envoy proxies

## Extending the PoC

This PoC can be extended in several ways:

1. **Add more workloads**: Register additional services with SPIRE
2. **Enhance policies**: Add more complex authorization rules in OPA
3. **Add monitoring**: Integrate with observability tools
4. **Implement credential rotation**: Add automatic credential rotation

## References

- [SPIFFE/SPIRE Documentation](https://spiffe.io/docs/latest/)
- [Envoy Proxy Documentation](https://www.envoyproxy.io/docs/envoy/latest/)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)