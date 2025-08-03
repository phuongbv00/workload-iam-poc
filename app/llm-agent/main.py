import json
import os
from typing import Dict, List, Optional

import requests


class LLMAgent:
    """
    A simple LLM agent that interacts with the User Management API.
    In a real-world scenario, this would integrate with an actual LLM,
    but for this PoC, we'll simulate the agent's behavior.
    """

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the LLM agent with the API base URL.

        In a production environment with Envoy, this would typically be:
        http://localhost:9901 (Envoy proxy address)
        """
        self.api_base_url = api_base_url
        self.session = requests.Session()

        # In a real implementation with SPIFFE/SPIRE, the agent would
        # obtain its identity automatically. For this PoC, we'll simulate it.
        self.agent_id = "spiffe://example.org/agent/llm-agent"

        print(f"LLM Agent initialized with ID: {self.agent_id}")
        print(f"API base URL: {self.api_base_url}")

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make an HTTP request to the API through the Envoy proxy.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request payload (for POST/PUT)

        Returns:
            API response as a dictionary
        """
        url = f"{self.api_base_url}{endpoint}"

        # In a real implementation with SPIFFE/SPIRE and Envoy,
        # the SPIFFE ID would be automatically included in mTLS
        # Here we simulate by adding a header
        headers = {
            "X-Forwarded-Client-Cert": f"By=spiffe://example.org/service/user-service;URI={self.agent_id}",
            "Content-Type": "application/json"
        }

        try:
            if method == "GET":
                response = self.session.get(url, headers=headers)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check if the request was successful
            response.raise_for_status()

            # For DELETE requests that return no content
            if response.status_code == 204:
                return {"status": "success"}

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return {"error": str(e)}

    def get_users(self) -> List[Dict]:
        """Get all users from the API"""
        response = self._make_request("GET", "/users")
        return response if isinstance(response, list) else []

    def get_user(self, user_id: str) -> Dict:
        """Get a specific user by ID"""
        return self._make_request("GET", f"/users/{user_id}")

    def create_user(self, name: str, email: str, role: str = "user") -> Dict:
        """Create a new user"""
        data = {"name": name, "email": email, "role": role}
        return self._make_request("POST", "/users", data)

    def update_user(self, user_id: str, name: str, email: str, role: str) -> Dict:
        """Update an existing user"""
        data = {"name": name, "email": email, "role": role}
        return self._make_request("PUT", f"/users/{user_id}", data)

    def delete_user(self, user_id: str) -> Dict:
        """Delete a user"""
        return self._make_request("DELETE", f"/users/{user_id}")

    def run_demo(self):
        """Run a demonstration of the agent's capabilities"""
        print("\n=== LLM Agent Demo ===\n")

        # Create a few users
        print("Creating users...")
        user1 = self.create_user("Alice Smith", "alice@example.com", "admin")
        print(f"Created user: {json.dumps(user1, indent=2)}")

        user2 = self.create_user("Bob Johnson", "bob@example.com", "user")
        print(f"Created user: {json.dumps(user2, indent=2)}")

        # Get all users
        print("\nGetting all users...")
        users = self.get_users()
        print(f"All users: {json.dumps(users, indent=2)}")

        # Get a specific user
        print(f"\nGetting user {user1['id']}...")
        user = self.get_user(user1['id'])
        print(f"User details: {json.dumps(user, indent=2)}")

        # Update a user
        print(f"\nUpdating user {user2['id']}...")
        updated_user = self.update_user(user2['id'], "Bob Smith", "bob.smith@example.com", "manager")
        print(f"Updated user: {json.dumps(updated_user, indent=2)}")

        # Delete a user
        print(f"\nDeleting user {user1['id']}...")
        result = self.delete_user(user1['id'])
        print(f"Delete result: {json.dumps(result, indent=2)}")

        # Verify deletion
        print("\nGetting all users after deletion...")
        users = self.get_users()
        print(f"All users: {json.dumps(users, indent=2)}")

        print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # In a real deployment, this would connect to the Envoy proxy
    # For direct testing without Envoy, we can connect to the API directly
    # Use API_BASE_URL environment variable or fall back to default
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    agent = LLMAgent(api_base_url=api_base_url)
    agent.run_demo()
