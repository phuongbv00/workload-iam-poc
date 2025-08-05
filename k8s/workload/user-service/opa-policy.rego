package envoy.authz

import input.attributes.request.http as http_request
import input.attributes.source.address as source_address
import input.attributes.source.certificate as client_cert

default allow = false

# Extract SPIFFE ID from client certificate
spiffe_id = client_id if {
    # Extract URI SAN from certificate
    [_, _, uri_type_and_value] := split(client_cert, ";")
    [_, uri] := split(uri_type_and_value, "=")
    client_id := uri
}

# Allow access to root endpoint for all authenticated clients
allow if {
    http_request.path == "/"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
}

# Allow access to users listing for LLM agent
allow if {
    http_request.path == "/users"
    http_request.method == "GET"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
}

# Allow access to specific user for LLM agent
allow if {
    startswith(http_request.path, "/users/")
    http_request.method == "GET"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
}

# Allow user creation for LLM agent
allow if {
    http_request.path == "/users"
    http_request.method == "POST"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"

    # Optional: Add content validation if needed
    # body := json.unmarshal(http_request.body)
    # body.role == "user" # Only allow creating users with role "user"
}

# Allow user update for LLM agent
allow if {
    startswith(http_request.path, "/users/")
    http_request.method == "PUT"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
}

# Allow user deletion for LLM agent
allow if {
    startswith(http_request.path, "/users/")
    http_request.method == "DELETE"
    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
}

# Log all authorization decisions
log_decision if {
    spiffe_id_value := spiffe_id
    method := http_request.method
    path := http_request.path
    decision := allow

    trace(sprintf("Authorization decision: %v for %v %v by %v", [decision, method, path, spiffe_id_value]))
}
