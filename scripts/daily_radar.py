#!/usr/bin/env python3
"""
Autonomous Daily Architecture Radar & Profile Updater
Updates shenald-dev/README.md with daily engineering insights.
Engine Priority:
1. GitHub Copilot CLI (inbuilt)
2. OpenRouter API with verified free model
3. Autonomous Deterministic Engineering Engine (guaranteed fallback for 100% streak reliability)
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Target file path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, "README.md")

# OpenRouter API key retrieved strictly from environment/secret
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Free models available on OpenRouter
FREE_MODELS = [
    "nvidia/nemotron-3.5-lightning:free",
    "liquid/lfm-3-1.7b:free",
    "particle-ai/particle-1:free",
    "recursive/flint-v1.0:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
]

# Curated high-level autonomous systems & architecture matrix (Offline Fallback Engine)
OFFLINE_RADAR_MATRIX = [
    {
        "quote": "The best architectures don't just scale computation; they bound complexity and guarantee invariants under chaos.",
        "focus": "Zero-Copy AST Invariants & Edge Verification",
        "pattern": "Dual Astrocyte-Neuron Reflex Loop",
        "takeaway": "Validate code at the syntax tree before compilation; treat agentic outputs as untrusted execution graphs."
    },
    {
        "quote": "Latency is the silent killer of autonomous agent loops; strip bloat at the PTY boundary before the LLM sees it.",
        "focus": "Terminal Stream Compaction & Zero-Token Lenses",
        "pattern": "Stream-Level Semantic Compactor",
        "takeaway": "Prune 95%+ of terminal noise at sub-millisecond speeds to preserve context fidelity and token economics."
    },
    {
        "quote": "Stateful distributed workflows demand deterministic replay, not optimistic retries.",
        "focus": "DAG Orchestration & Non-Circular State Propagation",
        "pattern": "Domain-Driven Immutable DAG Engine",
        "takeaway": "Isolate pipeline steps into pure functions; state transitions should be fully replayable from incident logs."
    },
    {
        "quote": "Micro-models on consumer silicon beat cloud monoliths when fine-tuned strictly for constrained edge domains.",
        "focus": "Edge Model Distillation & Zero-OOM Guards",
        "pattern": "Quantized PEFT Edge Collective",
        "takeaway": "Pair 1B-parameter distilled models with deterministic symbol engines (SymPy/AST) to achieve zero hallucination."
    },
    {
        "quote": "Observability for autonomous agents requires capturing the token waterfall, not just HTTP status codes.",
        "focus": "Passive Agent Stream Inspection & Firewalls",
        "pattern": "Reverse-Proxy Agentic Wireshark",
        "takeaway": "Intercept destructive commands at the protocol layer before an agent executes irreversible mutations."
    },
    {
        "quote": "Fast static blast radius analysis turns architectural uncertainty into verified commit confidence.",
        "focus": "Topological Call Graph Traversal",
        "pattern": "AST Invariant Radar",
        "takeaway": "Map cross-package dependency cascades before pushing code generated through vibecoding."
    },
    {
        "quote": "True system resilience lies in lightning-fast process isolation and ruthless resource reaping.",
        "focus": "Process Tree Containment & Zombie Reaping",
        "pattern": "Ephemeral Hyper-Proxy Cockpit",
        "takeaway": "Bind microservices into isolated OS job containers to guarantee zero orphaned background tasks."
    }
]


def prompt_text() -> str:
    return (
        "You are the autonomous system intelligence for Shenald's GitHub profile "
        "(Senior Software Architect & Autonomous AI Systems Engineer). "
        "Generate today's architecture dispatch in valid JSON format: "
        "{\n"
        '  "quote": "A punchy, profound 1-sentence engineering or AI architecture principle",\n'
        '  "focus": "Today\'s engineering focus area (3-5 words)",\n'
        '  "pattern": "Architectural pattern or invariant concept of the day",\n'
        '  "takeaway": "A 1-sentence pragmatic architectural takeaway"\n'
        "}\n"
        "Return ONLY the raw JSON object, without markdown quotes or explanation."
    )


def parse_json_response(raw_text: str):
    """Safely extracts JSON from an LLM response."""
    if not raw_text:
        return None
    # Remove code blocks if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if all(k in data for k in ["quote", "focus", "pattern", "takeaway"]):
                return data
        except Exception:
            pass
    return None


def try_copilot():
    """Attempt generation via inbuilt GitHub Copilot CLI."""
    print(">> [Engine 1] Attempting GitHub Copilot CLI...")
    commands_to_try = [
        ["copilot", "-p", prompt_text(), "-s"],
        ["gh", "copilot", "-p", prompt_text()],
    ]

    for cmd in commands_to_try:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                shell=(os.name == "nt")
            )
            output = proc.stdout.strip()
            err = proc.stderr.strip().lower()

            if proc.returncode == 0 and output:
                # Check if output contains error or rate limit
                if any(kw in output.lower() or kw in err for kw in ["credit", "limit", "rate", "unauthorized", "quota", "not found"]):
                    print(f"   Copilot reported limit/auth issue: {err or output}")
                    continue
                parsed = parse_json_response(output)
                if parsed:
                    print("   Successfully generated via GitHub Copilot!")
                    return parsed, "GitHub Copilot (Inbuilt)"
            else:
                print(f"   Command '{cmd[0]}' exited with code {proc.returncode}: {err[:100]}")
        except FileNotFoundError:
            print(f"   '{cmd[0]}' not installed or not in PATH.")
        except Exception as e:
            print(f"   Copilot attempt failed: {e}")

    print("   Copilot CLI unavailable or credits exhausted.")
    return None, None


def try_openrouter():
    """Attempt generation via OpenRouter API with free models."""
    print(">> [Engine 2] Attempting OpenRouter API (Fallback)...")
    api_key = os.environ.get("OPENROUTER_API_KEY") or OPENROUTER_API_KEY
    if not api_key:
        print("   No OPENROUTER_API_KEY found in environment.")
        return None, None

    for model in FREE_MODELS:
        print(f"   Testing free model: {model}...")
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/shenald-dev/shenald-dev",
                    "X-Title": "Shenald GitHub Daily Radar",
                },
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a senior software architect. Output only raw JSON."},
                        {"role": "user", "content": prompt_text()},
                    ],
                }).encode("utf-8")
            )

            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    parsed = parse_json_response(content)
                    if parsed:
                        print(f"   Successfully generated via OpenRouter ({model})!")
                        return parsed, f"OpenRouter [{model}]"
                    else:
                        print(f"   Model returned non-JSON response: {content[:80]}")
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
            except Exception:
                pass
            print(f"   Model {model} failed with HTTP {e.code}: {err_msg[:80]}")
        except Exception as e:
            print(f"   Model {model} error: {e}")

    print("   OpenRouter free tier currently unavailable or rate-limited.")
    return None, None


def try_offline_engine():
    """Deterministic fallback to guarantee 100% streak preservation."""
    print(">> [Engine 3] Using Autonomous Deterministic Architecture Engine...")
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    entry = OFFLINE_RADAR_MATRIX[day_of_year % len(OFFLINE_RADAR_MATRIX)]
    return entry, "Autonomous Architecture Engine (Deterministic)"


def generate_radar_card(data: dict, engine_name: str) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    quote = data.get("quote", "").strip()
    focus = data.get("focus", "").strip()
    pattern = data.get("pattern", "").strip()
    takeaway = data.get("takeaway", "").strip()

    # Completely invisible in GitHub markdown rendering.
    # Guarantees daily git diff for 100% streak retention without altering UI appearance.
    comment = f"""<!--
  AUTONOMOUS_STREAK_SYNC:START
  Last Synced: {now_utc}
  Engine: {engine_name}
  Focus: {focus}
  Pattern: {pattern}
  Quote: "{quote}"
  Takeaway: {takeaway}
  AUTONOMOUS_STREAK_SYNC:END
-->"""
    return comment


def update_readme():
    print(f"Reading target README: {README_PATH}")
    if not os.path.exists(README_PATH):
        print(f"Error: README.md not found at {README_PATH}")
        sys.exit(1)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean up any legacy visible DAILY_RADAR card if present
    content = re.sub(r"\n*<!-- DAILY_RADAR:START -->.*?<!-- DAILY_RADAR:END -->\n*", "\n", content, flags=re.DOTALL)

    # Step 1: Copilot
    data, engine = try_copilot()

    # Step 2: OpenRouter
    if not data:
        data, engine = try_openrouter()

    # Step 3: Offline Matrix
    if not data:
        data, engine = try_offline_engine()

    radar_comment = generate_radar_card(data, engine)

    # Update or append invisible streak sync block at the end of README
    sync_pattern = r"<!--\s*AUTONOMOUS_STREAK_SYNC:START.*?AUTONOMOUS_STREAK_SYNC:END\s*-->"
    if re.search(sync_pattern, content, flags=re.DOTALL):
        updated_content = re.sub(sync_pattern, radar_comment, content, flags=re.DOTALL)
        print("Updated existing invisible streak sync block in README.md")
    else:
        updated_content = content.rstrip() + "\n\n" + radar_comment + "\n"
        print("Appended invisible streak sync block to end of README.md")

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print("Successfully wrote clean README.md.")


if __name__ == "__main__":
    update_readme()
