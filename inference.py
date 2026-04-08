import requests
import os

# Use validator-provided API base OR local fallback
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

# ---------------- RESET ----------------
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)

    # Fail fast if HTTP error
    if r.status_code != 200:
        raise ValueError(f"Reset failed: HTTP {r.status_code}")

    data = r.json()

except Exception as e:
    print("Reset failed:", e)
    raise

total_reward = 0

# ---------------- SPAM LOGIC ----------------
spam_keywords = [
    "win", "free", "lottery", "prize",
    "offer", "urgent", "claim", "congratulations"
]

for step in range(3):

    # -------- SAFE STATE ACCESS --------
    state = data.get("state", {})

    email_text = state.get("email")

    if not email_text:
        print("Invalid response received:", data)
        raise ValueError("Email not found in state")

    # -------- DECISION --------
    if any(word in email_text.lower() for word in spam_keywords):
        action = {"action": 1}   # spam
    else:
        action = {"action": 0}   # not spam

    # -------- STEP CALL --------
    try:
        r = requests.post(f"{BASE_URL}/step", json=action, timeout=10)

        if r.status_code != 200:
            raise ValueError(f"Step failed: HTTP {r.status_code}")

        res = r.json()

    except Exception as e:
        print("Step failed:", e)
        raise

    # -------- REWARD --------
    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    # Update state for next loop
    data = res

    # Stop early if environment ends
    if res.get("done"):
        break

print(f"[END] total_reward={total_reward}")