import os
import requests
from openai import OpenAI

print("[START]")

# 🔥 FORCE USING ENV (NO .get())
client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"]
)

def get_action(email_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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

        # Ensure integer output
        if "1" in result:
            return 1
        return 0

    except Exception as e:
        print("LLM ERROR:", e)
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
            print("ERROR:", e)

    print("\nTOTAL REWARD:", total_reward)


if __name__ == "__main__":
    main()