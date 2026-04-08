import requests
import os

# Use API_BASE_URL in validator, fallback for local testing
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

# Reset environment safely
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print("Reset failed:", e)
    raise

total_reward = 0

# Improved spam detection
spam_keywords = [
    "win", "free", "lottery", "prize",
    "offer", "urgent", "claim", "congratulations"
]

for step in range(3):
    # ✅ SAFE access (prevents KeyError)
    email_text = data.get("state", {}).get("email")

    if not email_text:
        print("Unexpected response:", data)
        raise ValueError("Missing email in response")

    # Rule-based spam detection
    if any(word in email_text.lower() for word in spam_keywords):
        action = {"action": 1}
    else:
        action = {"action": 0}

    try:
        r = requests.post(f"{BASE_URL}/step", json=action, timeout=10)
        r.raise_for_status()
        res = r.json()
    except Exception as e:
        print("Step failed:", e)
        raise

    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    data = res  # update state

    if res.get("done"):
        break

print(f"[END] total_reward={total_reward}")