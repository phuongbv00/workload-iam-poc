import json
import os
from typing import Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from openai import OpenAI

FUNCTION_DEFINITIONS = [
    {
        "name": "create_user",
        "description": "Tạo mới một người dùng với tên, email và vai trò.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Tên của người dùng"},
                "email": {"type": "string", "description": "Email của người dùng"},
                "role": {"type": "string", "description": "Vai trò (user/admin)"}
            },
            "required": ["name", "email", "role"]
        }
    },
    {
        "name": "get_user",
        "description": "Lấy thông tin người dùng theo ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "ID của người dùng cần lấy"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_users",
        "description": "Lấy danh sách tất cả người dùng.",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "update_user",
        "description": "Cập nhật thông tin người dùng.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "ID của người dùng cần cập nhật"},
                "name": {"type": "string", "description": "Tên mới"},
                "email": {"type": "string", "description": "Email mới"},
                "role": {"type": "string", "description": "Vai trò mới"}
            },
            "required": ["user_id", "name", "email", "role"]
        }
    },
    {
        "name": "delete_user",
        "description": "Xóa người dùng theo ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "ID của người dùng cần xóa"}
            },
            "required": ["user_id"]
        }
    },
]


def call_llm_and_route(user_input: str) -> (Optional[str], Optional[Dict]):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": user_input}],
        functions=FUNCTION_DEFINITIONS,
        function_call="auto"
    )
    message = resp.choices[0].message
    if message.function_call:
        name = message.function_call.name
        args = json.loads(message.function_call.arguments)
        return name, args
    return None, None


class LLMAgent:
    def __init__(self, api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")):
        self.api_base_url = api_base_url
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        try:
            if method == "GET":
                r = self.session.get(url, headers=headers)
            elif method == "POST":
                r = self.session.post(url, headers=headers, json=data)
            elif method == "PUT":
                r = self.session.put(url, headers=headers, json=data)
            elif method == "DELETE":
                r = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            r.raise_for_status()
            return {} if r.status_code == 204 else r.json()
        except requests.RequestException as e:
            return {"error": str(e)}

    def get_users(self) -> List[Dict]:
        return self._make_request("GET", "/users") or []

    def get_user(self, user_id: str) -> Dict:
        return self._make_request("GET", f"/users/{user_id}")

    def create_user(self, name: str, email: str, role: str = "user") -> Dict:
        return self._make_request("POST", "/users", {"name": name, "email": email, "role": role})

    def update_user(self, user_id: str, name: str, email: str, role: str) -> Dict:
        return self._make_request("PUT", f"/users/{user_id}", {"name": name, "email": email, "role": role})

    def delete_user(self, user_id: str) -> Dict:
        return self._make_request("DELETE", f"/users/{user_id}")


app = FastAPI()


@app.post("/invoke")
def invoke():
    default_text = 'Tôi muốn tạo user mới thông tin là "Alice Smith", "alice@example.com", "admin"'
    func_name, func_args = call_llm_and_route(default_text)
    if not func_name:
        raise HTTPException(status_code=400, detail="LLM không xác định được function call.")
    agent = LLMAgent()
    if not hasattr(agent, func_name):
        raise HTTPException(status_code=400, detail=f"Function '{func_name}' không tồn tại.")
    result = getattr(agent, func_name)(**func_args)
    return {"input": default_text, "function_called": func_name, "arguments": func_args, "result": result}


@app.get("/demo")
def demo():
    agent = LLMAgent()
    outputs = []
    u1 = agent.create_user("Alice Smith", "alice@example.com", "admin")
    outputs.append({"action": "create_user", "output": u1})
    u2 = agent.create_user("Bob Johnson", "bob@example.com", "user")
    outputs.append({"action": "create_user", "output": u2})
    outputs.append({"action": "get_users", "output": agent.get_users()})
    outputs.append({"action": "get_user", "output": agent.get_user(u1.get("id"))})
    outputs.append({"action": "update_user",
                    "output": agent.update_user(u2.get("id"), "Bob Smith", "bob.smith@example.com", "manager")})
    outputs.append({"action": "delete_user", "output": agent.delete_user(u1.get("id"))})
    outputs.append({"action": "get_users", "output": agent.get_users()})
    return outputs


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
