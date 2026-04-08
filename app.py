from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

state = {
    "email": "win free money now",
    "step": 0
}

class ActionRequest(BaseModel):
    action: int


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/reset")
def reset():
    global state
    state = {
        "email": "win free money now",
        "step": 0
    }
    return {"state": state}


@app.post("/step")
def step(req: ActionRequest):
    global state

    reward = 1 if req.action == 1 else 0

    state["step"] += 1
    state["email"] = "normal message"

    return {
        "state": state,
        "reward": reward
    }