from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ActionRequest(BaseModel):
    action: int

# Initial state
def get_initial_state():
    return {
        "email": "win free money now",
        "step": 0
    }

state = get_initial_state()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/reset")
def reset():
    global state
    state = get_initial_state()
    return {"state": state}

@app.post("/step")
def step(req: ActionRequest):
    global state

    # Reward logic
    reward = 1 if req.action == 1 else 0

    # Update state safely
    state["step"] += 1

    # Change email to simulate environment
    if state["step"] % 2 == 0:
        state["email"] = "win free money now"
    else:
        state["email"] = "normal message"

    return {
        "state": state,
        "reward": reward
    }