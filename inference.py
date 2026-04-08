import os
import requests
from openai import OpenAI

print("[START]")
BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

print("API_BASE_URL:", BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# ❗ DO NOT SKIP — always attempt to create client
client = None

if BASE_URL and API_KEY:
    try:
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        print("[INFO] LLM client ready")
    except Exception as e:
        print("[ERROR] Client init failed:", e)


def get_action(email_text):
    # ❗ MUST TRY LLM FIRST
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Return 0 or 1 only"},
                    {"role": "user", "content": email_text}
                ]
            )

            return int(response.choices[0].message.content.strip())

        except Exception as e:
            print("[ERROR] LLM call failed:", e)

    # ❗ fallback ONLY if LLM fails
    return 0


def main():
    total_reward = 0

    for step in range(3):
        print(f"\n[STEP {step}]")

        try:
            r = requests.post("http://localhost:7860/reset")
            data = r.json()

            email = data["state"]["email"]
            print("Email:", email)

            action = get_action(email)
            print("ACTION:", action)

            r = requests.post(
                "http://localhost:7860/step",
                json={"action": action}
            )

            result = r.json()
            reward = result.get("reward", 0)

            print("REWARD:", reward)
            total_reward += reward

        except Exception as e:
            print("❌ Step failed:", e)

    print("\n[END] TOTAL REWARD:", total_reward)


if __name__ == "__main__":
    main()