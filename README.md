---
title: Email Spam Env
emoji: 📧
colorFrom: green
colorTo: yellow
sdk: docker
app_file: app.py
pinned: false
tags:
  - openenv
short_description: Email spam classification OpenEnv environment
---

# 📧 Email Spam Classification — OpenEnv Environment

An RL environment where an AI agent learns to classify emails as **spam** or **ham** (legitimate). The agent reads email metadata (subject, sender, body) and makes a binary decision at each step. Performance is measured by classification accuracy across curated real-world-style emails.

---

## 🎯 Motivation

Email spam detection is one of the most universally practiced real-world tasks. It requires nuanced reasoning about sender trust, linguistic cues, urgency signals, and contextual plausibility. This environment benchmarks an agent's ability to replicate this judgment — from obvious spam to sophisticated phishing.

---

## 🔌 API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Health check |
| `POST` | `/reset` | Start a new episode. Body: `{"task": "easy"}`. Returns initial observation. |
| `POST` | `/step`  | Submit action, receive next observation + reward |
| `GET`  | `/state` | Get current environment state |
| `GET`  | `/grade` | Get final score (0.0–1.0) for grading |

---

## 👁️ Observation Space

Each observation is a JSON object:

```json
{
  "email":   "string — body text of the email",
  "subject": "string — subject line",
  "sender":  "string — sender email address",
  "step":    "integer — current step number",
  "task":    "string — current task difficulty"
}
```

---

## 🎮 Action Space

```json
{ "action": 0 }   // 0 = HAM (legitimate email)
{ "action": 1 }   // 1 = SPAM
```

---

## 🏆 Reward Function

| Outcome | Reward |
|---------|--------|
| Correct classification | `1.0` |
| Incorrect classification | `0.0` |

**Episode score** = `correct_predictions / total_emails` (accuracy, 0.0–1.0)

The reward provides a signal at every step (not just at the end), enabling trajectory-level learning.

---

## 📋 Tasks

### Easy (`max_steps=3`)
Classify 3 emails with obvious spam signals — ALL CAPS subjects, prize claims, suspicious domains. Baseline accuracy: **0.67**

### Medium (`max_steps=5`)
Classify 5 emails including phishing attempts and borderline cases. Requires attention to sender domain mismatch and contextual plausibility. Baseline accuracy: **0.60**

### Hard (`max_steps=7`)
Classify 7 tricky emails: sophisticated phishing, cold sales outreach, and legitimate emails that superficially look suspicious. Challenges frontier LLMs. Baseline accuracy: **0.43**

---

## 🚀 Setup & Usage

### Local (Docker)
```bash
docker build -t email-spam-env .
docker run -p 7860:7860 email-spam-env
```

### Run baseline inference
```bash
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
export HF_TOKEN=your_token_here

python inference.py
```

### Quick API test
```bash
# Reset to easy task
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "easy"}'

# Submit action (1 = spam)
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"action": 1}'

# Get graded score
curl http://localhost:7860/grade
```

---

## 📊 Baseline Scores

| Task   | Score | Notes |
|--------|-------|-------|
| easy   | 0.67  | keyword heuristic baseline |
| medium | 0.60  | keyword heuristic baseline |
| hard   | 0.43  | keyword heuristic baseline |
| **avg**| **0.57** | — |

---

## 🧠 Inference Script Stdout Format

The `inference.py` emits structured logs per the OpenEnv spec. One `[START]` per task, one `[STEP]` per action, one `[END]` per task:

```
[START] task=easy env=email-spam-env model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=1 reward=1.00 done=false error=null
[STEP] step=2 action=0 reward=1.00 done=false error=null
[STEP] step=3 action=1 reward=0.00 done=true error=null
[END] success=true steps=3 score=0.67 rewards=1.00,1.00,0.00
```