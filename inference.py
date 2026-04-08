import os
import requests

print("[START]")

# ---------------- ENV ----------------
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ---------------- BASE URL ----------------
BASE_URL = API_BASE_URL if API_BASE_URL else "http://localhost:7860"

# ---------------- SAFE LLM CALL ----------------
def try_llm(email_text):
    if not API_BASE_URL or not API_KEY:
        print("⚠️ Skipping LLM (env not ready)")
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Classify email as spam (1) or not spam (0).

Email:
{email_text}

Respond ONLY with 0 or 1.
"""
                }
            ],
            max_tokens=5
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM ERROR:", e)
        return None

# ---------------- RESET ----------------
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    data = r.json()
except:
    data = {}

total_reward = 0

# ---------------- LOOP ----------------
for step in range(3):

    print(f"\n[STEP {step}]")

    email_text = data.get("state", {}).get("email", "")
    print("Email:", email_text)

    # -------- LLM FIRST --------
    result = try_llm(email_text)

    if result is not None:
        print("LLM RESULT:", result)
        action = 1 if "1" in result else 0
    else:
        # fallback ONLY if LLM fails
        print("⚠️ Using fallback")
        action = 1 if ("free" in email_text.lower() or "win" in email_text.lower()) else 0

    print("ACTION:", action)

    try:
        res = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            timeout=10
        ).json()
    except:
        res = {}

    reward = res.get("reward", 0)
    total_reward += reward

    print("REWARD:", reward)

    data = res

    if res.get("done"):
        break

print("\n[END] TOTAL REWARD:", total_reward)