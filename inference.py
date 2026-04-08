import requests
import os

# Base URL of the environment API
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")


def extract_email(data):
    """
    Safely extract email from different possible API response formats
    """
    if not isinstance(data, dict):
        return ""

    # Try multiple possible locations
    return (
        data.get("state", {}).get("email")
        or data.get("email")
        or data.get("obs", {}).get("email")
        or data.get("observation", {}).get("email")
        or ""
    )


def main():
    print("[START] Inference running...", flush=True)

    try:
        response = requests.post(f"{BASE_URL}/reset")
        data = response.json()
    except Exception as e:
        print("❌ ERROR: Cannot connect to API:", e, flush=True)
        return

    total_reward = 0

    for step in range(3):
        # 🔍 DEBUG OUTPUT (VERY IMPORTANT)
        print(f"\n--- STEP {step+1} ---", flush=True)
        print("RAW DATA:", data, flush=True)

        email = extract_email(data)

        print("Extracted Email:", email, flush=True)

        # Simple spam classifier logic
        if any(word in email.lower() for word in ["win", "free", "offer"]):
            action = "spam"
        else:
            action = "ham"

        print("Action:", action, flush=True)

        try:
            response = requests.post(
                f"{BASE_URL}/step",
                json={"action": action}
            )
            data = response.json()
        except Exception as e:
            print("❌ ERROR during step:", e, flush=True)
            break

        reward = data.get("reward", 0)
        total_reward += reward

        print("Reward:", reward, flush=True)

        if data.get("done", False):
            print("✅ Episode finished early", flush=True)
            break

    print("\n🏁 TOTAL REWARD:", total_reward, flush=True)


# ⚠️ REQUIRED ENTRY POINT (FIXES VALIDATION ERROR)
if __name__ == "__main__":
    main()