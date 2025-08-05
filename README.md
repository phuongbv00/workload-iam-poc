# Workload IAM Proof of Concept

This repository contains a proof of concept implementation of Workload Identity and Access Management (IAM) for a system
where an LLM agent needs to access a REST API.

Architecture:

1. **LLM Agent**: A Python application that simulates an LLM-based system making requests to a user management API.
2. **User Management API**: A FastAPI application that provides CRUD operations for user data.
3. **SPIFFE/SPIRE**: Provides workload identity management.
4. **Envoy Proxies**: Act as sidecars for both the agent and API, handling mTLS communication.
5. **Open Policy Agent (OPA)**: Enforces access control policies based on the workload identity.

[Quickstart with K8s](./k8s)
