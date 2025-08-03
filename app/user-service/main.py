import uuid

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

app = FastAPI(title="User Management API")

# Simple in-memory database for demonstration
users_db = {}


class User(BaseModel):
    id: str
    name: str
    email: str
    role: str


class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"


# Middleware to log requests and check headers
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log the request
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")

    # Continue processing the request
    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    return {"message": "User Management API"}


@app.get("/users", response_model=list[User])
def get_users():
    return list(users_db.values())


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    new_user = User(id=user_id, **user.model_dump())
    users_db[user_id] = new_user
    return new_user


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = User(id=user_id, **user.model_dump())
    users_db[user_id] = updated_user
    return updated_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")

    del users_db[user_id]
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
