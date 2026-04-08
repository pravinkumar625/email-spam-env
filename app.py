import os
import requests

print("[START]")

# ---------------- SAFE IMPORT ----------------
try:
    from openai import OpenAI
except Exception as e:
    print("❌ OpenAI import failed:", e)
    OpenAI = None

# ---------------- ENV ----------------
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ---------------- INIT CLIENT ----------------
client = None
if OpenAI and API_BASE_URL and API_KEY:
    try:
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )
        print("[INFO] LLM proxy initialized")
    except Exception as e:
        print("LLM init failed:", e)

# ---------------- BASE URL ----------------
BASE_URL = API_BASE_URL if API_BASE_URL else "http://localhost:7860"

# ---------------- RESET ----------------
try:
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    data = r.json()
    print("[INFO] Reset successful")
except Exception as e:
    print("Reset failed:", e)
    data = {}

total_reward = 0

# ---------------- LOOP ----------------
for step in range(3):

    print(f"\n[STEP {step}]")

    state = data.get("state", {})
    email_text = state.get("email", "")

    print("Email:", email_text)

    action = 0

    # ---------------- LLM CALL ----------------
    try:
        if client:
            print("🔵 Calling LLM proxy...")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
Classify the email as spam (1) or not spam (0).

Email:
{email_text}

Respond ONLY with 0 or 1.
"""
                    }
                ],
                max_tokens=5
            )

            result = response.choices[0].message.content.strip()
            print("LLM OUTPUT:", result)

            action = 1 if "1" in result else 0

        else:
            print("⚠️ LLM not available, using fallback")

            if "free" in email_text.lower() or "win" in email_text.lower():
                action = 1
            else:
                action = 0

    except Exception as e:
        print("❌ LLM ERROR:", e)

        # fallback
        if "free" in email_text.lower() or "win" in email_text.lower():
            action = 1
        else:
            action = 0

    print("ACTION:", action)

    # ---------------- STEP ----------------
    try:
        r = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            timeout=10
        )

        res = r.json()
        print("STEP RESPONSE:", res)

    except Exception as e:
        print("Step failed:", e)
        res = {}

    reward = res.get("reward", 0)
    total_reward += reward

    data = res

    if res.get("done"):
        break

# ---------------- END ----------------
print("\n[END] TOTAL REWARD:", total_reward)