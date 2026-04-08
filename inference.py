import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

# Reset
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print("Reset failed:", e)
    raise

total_reward = 0

for step in range(3):
    email_text = data.get("state", {}).get("email")

    if not email_text:
        print("Invalid state response:", data)
        break

    # simple rule-based agent
    if "win" in email_text.lower() or "free" in email_text.lower():
        action = {"action": 1}
    else:
        action = {"action": 0}

    try:
        r = requests.post(f"{BASE_URL}/step", json=action, timeout=10)
        r.raise_for_status()
        res = r.json()
    except Exception as e:
        print("Step failed:", e)
        break

    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    data = res  # update state for next loop

    if res.get("done"):
        break

print(f"[END] total_reward={total_reward}")