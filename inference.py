import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

# -------- RESET ENV --------
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print("Reset failed:", e)
    raise

total_reward = 0

# Spam detection keywords
spam_keywords = [
    "win", "free", "lottery", "prize",
    "offer", "urgent", "claim", "congratulations"
]

for step in range(3):

    # -------- SAFE STATE HANDLING --------
    state = data.get("state", {})

    email_text = state.get("email")

    if not email_text:
        print("Invalid response (missing email):", data)
        raise ValueError("Email not found in state")

    # -------- SIMPLE SPAM LOGIC --------
    if any(word in email_text.lower() for word in spam_keywords):
        action = {"action": 1}
    else:
        action = {"action": 0}

    # -------- STEP REQUEST --------
    try:
        r = requests.post(f"{BASE_URL}/step", json=action, timeout=10)
        r.raise_for_status()
        res = r.json()
    except Exception as e:
        print("Step failed:", e)
        raise

    # -------- SAFE REWARD HANDLING --------
    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    # Update state for next iteration
    data = res

    # Stop if environment ends
    if res.get("done"):
        break

print(f"[END] total_reward={total_reward}")