import requests
import os

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")


def main():
    print("[START] Inference Running...", flush=True)

    try:
        r = requests.post(f"{BASE_URL}/reset")
        data = r.json()
    except Exception as e:
        print("❌ Failed to connect to API:", e, flush=True)
        return

    total_reward = 0

    for step in range(3):
        # 🔍 DEBUG: Always print response (VERY IMPORTANT)
        print("DEBUG RESPONSE:", data, flush=True)

        # ✅ SAFE extraction (prevents KeyError)
        email = (
            data.get("state", {}).get("email")
            or data.get("email")
            or data.get("obs", {}).get("email")
            or ""
        )

        print(f"Extracted email: {email}", flush=True)

        # Simple spam logic
        if "win" in email.lower() or "free" in email.lower():
            action = "spam"
        else:
            action = "ham"

        try:
            response = requests.post(
                f"{BASE_URL}/step",
                json={"action": action}
            )
            data = response.json()
        except Exception as e:
            print("❌ Step error:", e, flush=True)
            break

        reward = data.get("reward", 0)
        total_reward += reward

        print(f"Step {step+1} → action={action}, reward={reward}", flush=True)

        if data.get("done", False):
            break

    print("🏁 Total Reward:", total_reward, flush=True)


# ⚠️ REQUIRED ENTRY POINT (FIXES YOUR VALIDATION ERROR)
if __name__ == "__main__":
    main()