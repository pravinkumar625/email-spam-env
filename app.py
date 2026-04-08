from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

emails = [
    {"text": "Win a free iPhone now!", "label": 1},
    {"text": "Meeting at 10am tomorrow", "label": 0},
    {"text": "Congratulations! You won a lottery", "label": 1},
    {"text": "Project deadline extended", "label": 0},
]

state_data = {}

class Action(BaseModel):
    action: int  # 0 = not spam, 1 = spam

@app.post("/reset")
def reset():
    global state_data
    email = random.choice(emails)

    state_data = {
        "email": email["text"],
        "label": email["label"],
        "step": 0,
        "total_reward": 0
    }

    return {"state": state_data}

@app.post("/step")
def step(action: Action):
    global state_data

    correct = state_data["label"]

    reward = 1.0 if action.action == correct else 0.0

    state_data["step"] += 1
    state_data["total_reward"] += reward

    done = state_data["step"] >= 3

    return {
        "state": state_data,
        "reward": reward,
        "done": done
    }

@app.get("/state")
def state():
    return state_data