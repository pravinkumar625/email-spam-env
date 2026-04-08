import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")


def main():
    print("[START] OpenEnv Agent Running")

    try:
        r = requests.post(f"{BASE_URL}/reset")
        data = r.json()
    except Exception as e:
        print("Error connecting to API:", e)
        return

    total_reward = 0

    for step in range(3):
        email_text = data["state"]["email"]

        # Simple rule-based agent (you can improve this)
        if "win" in email_text.lower() or "free" in email_text.lower():
            action = "spam"
        else:
            action = "ham"

        try:
            response = requests.post(f"{BASE_URL}/step", json={"action": action})
            data = response.json()
        except Exception as e:
            print("Step error:", e)
            break

        reward = data.get("reward", 0)
        total_reward += reward

        print(f"Step {step+1}: action={action}, reward={reward}")

        if data.get("done", False):
            break

    print("Total Reward:", total_reward)


# REQUIRED ENTRY POINT FOR DEPLOYMENT
if __name__ == "__main__":
    main()