import os
import requests
from openai import OpenAI

print("[START]")

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

def get_action(email_text):
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",  # safer for proxy
        messages=[
            {
                "role": "system",
                "content": "You are a spam classifier. Respond ONLY with 0 or 1."
            },
            {
                "role": "user",
                "content": email_text
            }
        ]
    )

    result = response.choices[0].message.content.strip()
    print("LLM RAW:", result)

    if result == "1":
        return 1
    return 0


def main():
    total_reward = 0

    for step in range(3):
        print(f"\n[STEP {step}]")

        r = requests.post(f"{BASE_URL}/reset")
        data = r.json()

        email = data["state"]["email"]
        print("Email:", email)

        action = get_action(email)
        print("ACTION:", action)

        r = requests.post(
            f"{BASE_URL}/step",
            json={"action": action}
        )

        result = r.json()
        reward = result.get("reward", 0)

        print("REWARD:", reward)
        total_reward += reward

    print("\nTOTAL REWARD:", total_reward)


if __name__ == "__main__":
    main()