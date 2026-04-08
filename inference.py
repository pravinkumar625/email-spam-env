import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

print("[START]")

r = requests.post(f"{BASE_URL}/reset")
data = r.json()

total_reward = 0

for step in range(3):
    email_text = data["state"]["email"]

    # simple rule-based agent
    if "win" in email_text.lower() or "free" in email_text.lower():
        action = {"action": 1}
    else:
        action = {"action": 0}

    r = requests.post(f"{BASE_URL}/step", json=action)
    res = r.json()

    reward = res["reward"]
    total_reward += reward

    print(f"[STEP] step={step} reward={reward}")

    if res["done"]:
        break

print(f"[END] total_reward={total_reward}")