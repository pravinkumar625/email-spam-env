import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

# -------- RESET (SAFE - DO NOT CRASH) --------
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)

    if r.status_code != 200:
        print(f"[WARNING] Reset returned HTTP {r.status_code}, continuing...")

    try:
        data = r.json()
    except Exception:
        print("[WARNING] Invalid JSON from reset, using fallback")
        data = {}

except Exception as e:
    print("[WARNING] Reset request failed:", e)
    data = {}

total_reward = 0

# -------- SPAM KEYWORDS --------
spam_keywords = [
    "win", "free", "lottery", "prize",
    "offer", "urgent", "claim", "congratulations"
]

for step in range(3):

    # -------- SAFE STATE --------
    state = data.get("state", {})

    email_text = state.get("email")

    # Fallback if no email
    if not email_text:
        email_text = "no email"

    # -------- DECISION --------
    if any(word in email_text.lower() for word in spam_keywords):
        action = {"action": 1}
    else:
        action = {"action": 0}

    # -------- STEP --------
    try:
        r = requests.post(f"{BASE_URL}/step", json=action, timeout=10)

        if r.status_code != 200:
            print(f"[WARNING] Step returned HTTP {r.status_code}")

        try:
            res = r.json()
        except Exception:
            print("[WARNING] Invalid JSON from step, using fallback")
            res = {}

    except Exception as e:
        print("[WARNING] Step request failed:", e)
        res = {}

    # -------- REWARD --------
    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    data = res

    if res.get("done"):
        break

print(f"[END] total_reward={total_reward}")