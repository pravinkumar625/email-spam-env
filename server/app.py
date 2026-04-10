import random
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Literal

app = FastAPI(title="Email Spam Classification OpenEnv")

# ---------------------------------------------------------------------------
# Typed Pydantic models (OpenEnv spec)
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    task: Optional[str] = "easy"   # accept task from JSON body OR query param

class Action(BaseModel):
    action: Literal[0, 1]          # 0 = ham, 1 = spam

# ---------------------------------------------------------------------------
# Email datasets per difficulty
# ---------------------------------------------------------------------------

TASKS = {
    "easy": {
        "max_steps": 3,
        "emails": [
            {"subject": "WIN FREE MONEY NOW!!!",
             "sender": "promo@spam.net",
             "body": "Congratulations! You have won $1,000,000. Click here to claim your prize NOW!",
             "label": 1},
            {"subject": "Meeting tomorrow",
             "sender": "boss@company.com",
             "body": "Hi, just a reminder that we have our weekly standup at 10am tomorrow.",
             "label": 0},
            {"subject": "FREE OFFER LIMITED TIME",
             "sender": "deals@freeoffers.biz",
             "body": "Act now! Free gift cards available for a limited time. Claim your free offer today!",
             "label": 1},
        ]
    },
    "medium": {
        "max_steps": 5,
        "emails": [
            {"subject": "Your account needs attention",
             "sender": "security@paypa1.com",
             "body": "We noticed unusual activity. Please verify your account by clicking the link below.",
             "label": 1},
            {"subject": "Quarterly report attached",
             "sender": "finance@company.com",
             "body": "Please find the Q3 financial report attached. Let me know if you have questions.",
             "label": 0},
            {"subject": "You've been selected!",
             "sender": "noreply@lottery-winners.net",
             "body": "Our records show you qualify for a special reward. Reply with your details to claim.",
             "label": 1},
            {"subject": "Lunch tomorrow?",
             "sender": "alice@gmail.com",
             "body": "Hey, want to grab lunch at the new Italian place on Main St? Around 12:30?",
             "label": 0},
            {"subject": "Invoice #4821 due",
             "sender": "billing@supplier.com",
             "body": "This is a reminder that invoice #4821 for $450 is due on Friday. Please arrange payment.",
             "label": 0},
        ]
    },
    "hard": {
        "max_steps": 7,
        "emails": [
            {"subject": "Following up on our conversation",
             "sender": "j.smith@consultancy-partners.com",
             "body": "Hi, it was great speaking with you at the conference. I'd love to explore synergies. Let's connect!",
             "label": 1},
            {"subject": "Your package could not be delivered",
             "sender": "delivery@ups-notification.com",
             "body": "We attempted to deliver your package. Please confirm your address to reschedule.",
             "label": 1},
            {"subject": "Project deadline update",
             "sender": "pm@realclient.io",
             "body": "The client moved the deadline to next Wednesday. Can the team accommodate this?",
             "label": 0},
            {"subject": "Exclusive offer for valued customers",
             "sender": "rewards@yourbank.com",
             "body": "As a valued customer, you qualify for a 0% APR offer. Activate it before it expires.",
             "label": 1},
            {"subject": "Re: Your job application",
             "sender": "hr@careers-portal.net",
             "body": "We reviewed your application. Please complete this skills assessment to proceed.",
             "label": 1},
            {"subject": "Code review request",
             "sender": "dev@teammate.io",
             "body": "Hey, I opened a PR for the auth refactor. Could you take a look when you get a chance?",
             "label": 0},
            {"subject": "Action required: subscription renewal",
             "sender": "billing@netflix.com",
             "body": "Your Netflix subscription renews on the 15th. No action needed if you want to continue.",
             "label": 0},
        ]
    }
}

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

state = {
    "task": "easy",
    "step": 0,
    "done": False,
    "score": 0.0,
    "correct": 0,
    "total": 0,
    "current_email_idx": 0,
    "emails": [],
    "max_steps": 3,
}


def make_state(task: str) -> dict:
    emails = TASKS[task]["emails"].copy()
    random.shuffle(emails)
    return {
        "task": task,
        "step": 0,
        "done": False,
        "score": 0.0,
        "correct": 0,
        "total": 0,
        "current_email_idx": 0,
        "emails": emails,
        "max_steps": TASKS[task]["max_steps"],
    }


def get_current_observation() -> dict:
    idx = state["current_email_idx"]
    if idx < len(state["emails"]):
        email = state["emails"][idx]
        return {
            "email":   email["body"],
            "subject": email["subject"],
            "sender":  email["sender"],
            "step":    state["step"],
            "task":    state["task"],
        }
    return {"email": "", "subject": "", "sender": "", "step": state["step"], "task": state["task"]}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "env": "email-spam-env", "version": "1.0"}


@app.post("/reset")
def reset(req: ResetRequest = None, task: str = "easy"):
    """
    Reset the environment. Accepts task in three ways (all optional, default=easy):
      - JSON body: {"task": "medium"}
      - Query param: POST /reset?task=medium
      - Empty body: POST /reset  (uses default 'easy')
    """
    global state

    # Resolve task: body > query param > default
    resolved_task = "easy"
    if req is not None and req.task in TASKS:
        resolved_task = req.task
    elif task in TASKS:
        resolved_task = task

    state = make_state(resolved_task)
    obs = get_current_observation()

    return {
        "observation": obs,
        "state": {k: v for k, v in state.items() if k != "emails"},  # don't leak all emails
    }


@app.post("/step")
def step(req: Action):
    global state

    if state["done"]:
        return {
            "observation": get_current_observation(),
            "reward": 0.0,
            "done": True,
            "info": {"message": "Episode already done. Call /reset."},
        }

    idx = state["current_email_idx"]
    email = state["emails"][idx]
    true_label = email["label"]

    correct = (req.action == true_label)
    reward  = 1.0 if correct else 0.0

    if correct:
        state["correct"] += 1
    state["total"] += 1
    state["step"]  += 1
    state["current_email_idx"] += 1

    done = (
        state["current_email_idx"] >= len(state["emails"])
        or state["step"] >= state["max_steps"]
    )
    state["done"] = done

    if done:
        state["score"] = state["correct"] / state["total"] if state["total"] > 0 else 0.0

    return {
        "observation": get_current_observation(),
        "reward":      reward,
        "done":        done,
        "info": {
            "true_label":      true_label,
            "correct":         correct,
            "accuracy_so_far": round(state["correct"] / state["total"], 4),
            "step":            state["step"],
        },
    }


@app.get("/state")
def get_state():
    return {
        "state":       {k: v for k, v in state.items() if k != "emails"},
        "observation": get_current_observation(),
    }


@app.get("/grade")
def grade():
    """Return final score in 0.0–1.0 range for the grader."""
    if state["total"] == 0:
        return {"score": 0.0, "correct": 0, "total": 0, "task": state["task"]}

    score = state["correct"] / state["total"]
    return {
        "score":   round(score, 4),
        "correct": state["correct"],
        "total":   state["total"],
        "task":    state["task"],
        "done":    state["done"],
    }