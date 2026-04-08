import os
import requests
from openai import OpenAI

BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

print("[START]")
print("API_BASE_URL:", BASE_URL)
print("API_KEY exists:", bool(API_KEY))

# DO NOT block execution if missing locally
client = None

try:
    if BASE_URL and API_KEY:
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY
        )
        print("[INFO] LLM client initialized")
    else:
        print("[WARN] Running without LLM (waiting for validator injection)")
except Exception as e:
    print("[ERROR] Failed to initialize client:", e)


def get_llm_action(email_text: str) -> int:
    """
    MUST use LLM when available.
    Never skip if client exists.
    """

    if not client:
        return 0  # fallback only if LLM truly unavailable

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Classify email: 1 = spam, 0 = not spam"
                },
                {
                    "role": "user",
                    "content": email_text
                }
            ]
        )

        result = response.choices[0].message.content.strip()

        return int(result)

    except Exception as e:
        print("[ERROR] LLM call failed:", e)
        return 0


def main():
    total_reward = 0

    for step in range(3):
        print(f"\n[STEP {step}]")

        try:
            r = requests.post("http://localhost:7860/reset")
            data = r.json()

            email_text = data["state"]["email"]
            print("Email:", email_text)

            action = get_llm_action(email_text)

            print("ACTION:", action)

            r = requests.post(
                "http://localhost:7860/step",
                json={"action": action}
            )

            data = r.json()

            reward = data.get("reward", 0)
            total_reward += reward

            print("REWARD:", reward)

        except Exception as e:
            print("❌ Step failed:", e)

    print("\n[END] TOTAL REWARD:", total_reward)


if __name__ == "__main__":
    main()