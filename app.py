import os
import requests
from openai import OpenAI

print("[START]")

# ---------------- ENV (MUST USE EXACTLY THESE) ----------------
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ---------------- VALIDATE ENV ----------------
if not API_BASE_URL or not API_KEY:
    print("❌ Missing API env variables")
    raise Exception("API_BASE_URL and API_KEY are required")

# ---------------- OPENAI CLIENT (IMPORTANT) ----------------
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY
)

# ---------------- BASE URL ----------------
BASE_URL = API_BASE_URL

# ---------------- RESET ----------------
r = requests.post(f"{BASE_URL}/reset")
data = r.json()

total_reward = 0

# ---------------- LOOP ----------------
for step in range(3):

    state = data.get("state", {})
    email_text = state.get("email", "")

    print(f"\n[STEP {step}] Email:", email_text)

    action = 0

    # ---------------- LLM CALL (MANDATORY FOR PASSING) ----------------
    try:
        print("🔵 Making LLM call...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Classify this email as spam (1) or not spam (0).

Email:
{email_text}

Respond ONLY with 0 or 1.
"""
                }
            ],
            max_tokens=5
        )

        result = response.choices[0].message.content.strip()
        print("LLM RAW OUTPUT:", result)

        action = 1 if "1" in result else 0

    except Exception as e:
        print("❌ LLM ERROR:", e)

        # fallback ONLY if LLM fails
        if "free" in email_text.lower() or "win" in email_text.lower():
            action = 1
        else:
            action = 0

    print("ACTION:", action)

    # ---------------- STEP ----------------
    r = requests.post(
        f"{BASE_URL}/step",
        json={"action": action}
    )

    res = r.json()

    print("STEP RESPONSE:", res)

    reward = res.get("reward", 0)
    total_reward += reward

    data = res

    if res.get("done"):
        break

# ---------------- END ----------------
print("\n[END] TOTAL REWARD:", total_reward)