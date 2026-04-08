import os
import requests

print("[START]")

# ---------------- ENV ----------------
API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY = os.environ.get("API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ---------------- CHECK ENV ----------------
if not API_BASE_URL or not API_KEY:
    raise Exception("❌ API_BASE_URL and API_KEY are missing (validator not injecting)")

# ---------------- STEP ----------------
def call_llm(email_text):
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

# ---------------- RESET ----------------
data = requests.post(f"{API_BASE_URL}/reset").json()

total_reward = 0

# ---------------- LOOP ----------------
for step in range(3):

    print(f"\n[STEP {step}]")

    email_text = data["state"]["email"]
    print("Email:", email_text)

    try:
        result = call_llm(email_text)
        print("LLM RESULT:", result)

        action = 1 if "1" in result else 0

    except Exception as e:
        print("LLM ERROR:", e)
        action = 0

    print("ACTION:", action)

    res = requests.post(
        f"{API_BASE_URL}/step",
        json={"action": action}
    ).json()

    reward = res.get("reward", 0)
    total_reward += reward

    print("REWARD:", reward)

    data = res

    if res.get("done"):
        break

print("\n[END] TOTAL REWARD:", total_reward)