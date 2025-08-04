import os
import json
import requests
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

# Load environment variables from .env

# ===============================
# 1) KHỞI TẠO OPENAI CLIENT
# ===============================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Missing OPENAI_API_KEY in environment")
client = OpenAI(api_key=api_key)

# Định nghĩa các hàm (functions) mà LLM được phép gọi
FUNCTION_DEFINITIONS = [
    {
        "name": "create_user",
        "description": "Tạo mới một người dùng với tên, email và vai trò.",
        "parameters": {
            "type": "object",
            "properties": {
                "name":  {"type": "string", "description": "Tên của người dùng"},
                "email": {"type": "string", "description": "Email của người dùng"},
                "role":  {"type": "string", "description": "Vai trò (user/admin)"}
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
                "name":    {"type": "string", "description": "Tên mới"},
                "email":   {"type": "string", "description": "Email mới"},
                "role":    {"type": "string", "description": "Vai trò mới"}
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
    """
    Gửi user_input cho OpenAI GPT-3.5 Turbo, nhận lại function_call nếu có,
    rồi parse và trả về tên hàm + args để gọi trong code.
    """
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
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


# ===============================
# CLASS LLMAgent
# ===============================
class LLMAgent:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session = requests.Session()
        self.agent_id = "spiffe://example.org/agent/llm-agent"

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "X-Forwarded-Client-Cert": f"By=spiffe://example.org/service/user-service;URI={self.agent_id}",
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


# ===============================
# FASTAPI APP
# ===============================
app = FastAPI()

# Request model cho LLM endpoint
class LLMRequest(BaseModel):
    text: str

@app.post("/invoke")
def invoke(request: LLMRequest):
    func_name, func_args = call_llm_and_route(request.text)
    if not func_name:
        raise HTTPException(status_code=400, detail="No function call detected from LLM.")
    agent = LLMAgent()
    if not hasattr(agent, func_name):
        raise HTTPException(status_code=400, detail=f"Function '{func_name}' not found.")
    result = getattr(agent, func_name)(**func_args)
    return {
        "function_called": func_name,
        "arguments": func_args,
        "result": result
    }

@app.get("/demo")
def demo():
    agent = LLMAgent()
    outputs = []

    # 1. Create two users
    u1 = agent.create_user("Alice Smith", "alice@example.com", "admin")
    outputs.append({"action": "create_user", "input": {"name": "Alice Smith", "email": "alice@example.com", "role": "admin"}, "output": u1})
    u2 = agent.create_user("Bob Johnson", "bob@example.com", "user")
    outputs.append({"action": "create_user", "input": {"name": "Bob Johnson", "email": "bob@example.com", "role": "user"}, "output": u2})

    # 2. Get all users
    all_users = agent.get_users()
    outputs.append({"action": "get_users", "output": all_users})

    # 3. Get specific user
    user_detail = agent.get_user(u1.get("id"))
    outputs.append({"action": "get_user", "input": {"user_id": u1.get("id")}, "output": user_detail})

    # 4. Update a user
    updated = agent.update_user(u2.get("id"), "Bob Smith", "bob.smith@example.com", "manager")
    outputs.append({"action": "update_user", "input": {"user_id": u2.get("id"), "name": "Bob Smith", "email": "bob.smith@example.com", "role": "manager"}, "output": updated})

    # 5. Delete a user
    deleted = agent.delete_user(u1.get("id"))
    outputs.append({"action": "delete_user", "input": {"user_id": u1.get("id")}, "output": deleted})

    # 6. Final list
    final_list = agent.get_users()
    outputs.append({"action": "get_users", "output": final_list})

    return outputs

@app.get("/start")
def start():
    """
    Endpoint test nhanh: giả lập call LLM và thực thi create_user.
    """
    test_input = 'Tôi muốn tạo user mới thông tin là "Alice Smith", "alice@example.com", "admin"'
    func_name, func_args = call_llm_and_route(test_input)
    if not func_name:
        raise HTTPException(status_code=400, detail="LLM không xác định được function call.")
    agent = LLMAgent()
    if not hasattr(agent, func_name):
        raise HTTPException(status_code=400, detail=f"Function '{func_name}' không tồn tại.")
    result = getattr(agent, func_name)(**func_args)
    return {"input": test_input, "function_called": func_name, "arguments": func_args, "result": result}
