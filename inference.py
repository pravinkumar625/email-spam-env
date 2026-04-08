import os
import requests
from openai import OpenAI

print("[START]")

# ---------------- ENV ----------------
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ---------------- LLM CLIENT ----------------
client = None
if API_BASE_URL and API_KEY:
    try:
        client = OpenAI(
            base_url=API_BASE_URL,
            api_key=API_KEY
        )
        print("[INFO] LLM proxy initialized")
    except Exception as e:
        print("LLM init failed:", e)
else:
    print("[WARN] Missing API env variables")

# ---------------- BASE URL ----------------
BASE_URL = API_BASE_URL if API_BASE_URL else "http://localhost:7860"

# ---------------- RESET ----------------
try:
    print("[INFO] Calling /reset")
    r = requests.post(f"{BASE_URL}/reset", timeout=10)
    r.raise_for_status()
    data = r.json()
    print("[INFO] Reset response received:", data)
except Exception as e:
    print("Reset failed:", e)
    data = {}

total_reward = 0

# ---------------- LOOP ----------------
for step in range(3):

    print(f"\n[INFO] ===== STEP {step} =====")

    state = data.get("state", {})
    email_text = state.get("email", "")

    print("Email:", email_text)

    action = 0  # default fallback

    # ---------------- LLM CALL ----------------
    try:
        if client and email_text:
            print("🔵 LLM CALL TRIGGERED")

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # safer for proxy
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Classify the email as spam (1) or not spam (0).\n\n"
                            f"Email: {email_text}\n\n"
                            "Respond ONLY with 0 or 1."
                        )
                    }
                ],
                max_tokens=5
            )

            output = response.choices[0].message.content.strip()

            print("LLM OUTPUT:", output)

            if "1" in output:
                action = 1
            else:
                action = 0

        else:
            print("⚠️ Using fallback (no LLM available)")

            if "free" in email_text.lower() or "win" in email_text.lower():
                action = 1
            else:
                action = 0

    except Exception as e:
        print("❌ LLM ERROR:", e)

        # fallback on error
        if "free" in email_text.lower() or "win" in email_text.lower():
            action = 1
        else:
            action = 0

    print("ACTION SELECTED:", action)

    # ---------------- STEP ----------------
    try:
        print("[INFO] Sending action to /step")

        r = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            timeout=10
        )

        print("Step status:", r.status_code)

        r.raise_for_status()
        res = r.json()

        print("Step response:", res)

    except Exception as e:
        print("❌ Step failed:", e)
        res = {}

    reward = res.get("reward", 0)
    total_reward += reward

    print(f"[STEP RESULT] reward={reward}")

    data = res

    if res.get("done"):
        print("[INFO] Episode finished early")
        break

# ---------------- END ----------------
print(f"\n[END] total_reward={total_reward}")