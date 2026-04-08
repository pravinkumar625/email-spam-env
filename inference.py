import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")


def extract_email(data):
    """Safely extract email from multiple possible formats"""
    if not isinstance(data, dict):
        return ""

    return (
        data.get("state", {}).get("email")
        or data.get("email")
        or data.get("obs", {}).get("email")
        or ""
    )


def main():
    print("[START] Running inference...", flush=True)

    try:
        r = requests.post(f"{BASE_URL}/reset")
        data = r.json()
    except Exception as e:
        print("❌ API connection failed:", e, flush=True)
        return

    total_reward = 0

    for step in range(3):
        print(f"\n--- STEP {step+1} ---", flush=True)
        print("RAW DATA:", data, flush=True)

        email = extract_email(data)
        print("EMAIL:", email, flush=True)

        # Simple spam detection
        if any(word in email.lower() for word in ["win", "free", "offer"]):
            action = "spam"
        else:
            action = "ham"

        print("ACTION:", action, flush=True)

        try:
            r = requests.post(f"{BASE_URL}/step", json={"action": action})
            data = r.json()
        except Exception as e:
            print("❌ Step error:", e, flush=True)
            break

        reward = data.get("reward", 0)
        total_reward += reward

        print("REWARD:", reward, flush=True)

        if data.get("done", False):
            break

    print("\n🏁 TOTAL REWARD:", total_reward, flush=True)


if __name__ == "__main__":
    main()