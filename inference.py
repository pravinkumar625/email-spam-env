"""
Inference Script — Email Spam Classification OpenEnv
=====================================================
MANDATORY environment variables:
    API_BASE_URL   The API endpoint for the LLM (must have default)
    MODEL_NAME     The model identifier (must have default)
    HF_TOKEN       Your Hugging Face API token (mandatory, no default)
    SPACE_URL      Base URL of THIS FastAPI environment server
                   Defaults to http://localhost:7860

STDOUT FORMAT (OpenEnv spec):
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
"""

import os
import requests
from typing import List, Optional
from openai import OpenAI

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN     = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# SPACE_URL points to THIS environment's FastAPI server — separate from LLM router.
SPACE_URL = os.getenv("SPACE_URL", "http://localhost:7860").rstrip("/")

BENCHMARK = "email-spam-env"
TASKS = ["easy", "medium", "hard"]
SUCCESS_SCORE_THRESHOLD = 0.5

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

SYSTEM_PROMPT = """You are an expert email spam classifier.

Given an email's subject, sender, and body — classify it as spam or ham.

Respond with ONLY one of:
  0   (ham — legitimate email)
  1   (spam)

No explanation. No punctuation. Just the digit 0 or 1."""


# ---------------------------------------------------------------------------
# Structured log helpers — exact format required by OpenEnv spec
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val  = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    # IMPORTANT: spec says [END] has: success, steps, rewards — NO score field
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)


# ---------------------------------------------------------------------------
# LLM classification
# ---------------------------------------------------------------------------

def classify_email(observation: dict) -> int:
    """Ask the LLM to classify an email. Returns 0 (ham) or 1 (spam)."""
    user_msg = (
        f"Subject: {observation.get('subject', 'N/A')}\n"
        f"Sender:  {observation.get('sender',  'N/A')}\n"
        f"Body:    {observation.get('email',   'N/A')}\n\n"
        "Reply with 0 (ham) or 1 (spam)."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=5,
            temperature=0.0,
        )
        raw = (response.choices[0].message.content or "").strip()
        digit = int(raw[0])
        return digit if digit in (0, 1) else 0
    except Exception:
        # Keyword fallback when LLM is unavailable
        text = f"{observation.get('subject','')} {observation.get('email','')}".lower()
        spam_words = ["win", "free", "offer", "prize", "click here", "claim",
                      "urgent", "lottery", "selected", "reward",
                      "congratulations", "verify"]
        return 1 if any(w in text for w in spam_words) else 0


# ---------------------------------------------------------------------------
# Run a single task episode
# ---------------------------------------------------------------------------

def run_task(task_name: str) -> dict:
    rewards: List[float] = []
    steps   = 0
    score   = 0.0
    success = False

    # [START] logged before anything can fail
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        # Reset environment
        try:
            r = requests.post(f"{SPACE_URL}/reset", json={"task": task_name}, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[DEBUG] Reset failed for task={task_name}: {e}", flush=True)
            return {"task": task_name, "score": 0.0, "steps": 0, "rewards": []}

        obs  = data.get("observation", {})
        done = False

        while not done:
            action    = classify_email(obs)
            error_msg = None

            try:
                r = requests.post(
                    f"{SPACE_URL}/step",
                    json={"action": action},
                    timeout=30,
                )
                r.raise_for_status()
                result = r.json()
            except Exception as e:
                error_msg = str(e)
                log_step(step=steps + 1, action=str(action), reward=0.0, done=True, error=error_msg)
                break

            reward = float(result.get("reward", 0.0))
            done   = bool(result.get("done", True))
            obs    = result.get("observation", {})
            steps += 1
            rewards.append(reward)

            log_step(step=steps, action=str(action), reward=reward, done=done, error=error_msg)

        # Fetch graded score from /grade endpoint
        try:
            g     = requests.get(f"{SPACE_URL}/grade", timeout=10).json()
            score = float(g.get("score", 0.0))
        except Exception:
            score = sum(rewards) / max(len(rewards), 1)

        score   = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        # [END] always emitted — spec format: no score= field
        log_end(success=success, steps=steps, rewards=rewards)

    return {"task": task_name, "score": score, "steps": steps, "rewards": rewards}


# ---------------------------------------------------------------------------
# Main — run all tasks
# ---------------------------------------------------------------------------

def main():
    all_results = []

    for task in TASKS:
        result = run_task(task)
        all_results.append(result)

    overall = sum(r["score"] for r in all_results) / len(all_results)

    print(f"\n🏁 OVERALL SCORE: {overall:.4f}", flush=True)
    for r in all_results:
        print(f"   {r['task']:8s} → score={r['score']:.4f}  steps={r['steps']}", flush=True)


if __name__ == "__main__":
    main()