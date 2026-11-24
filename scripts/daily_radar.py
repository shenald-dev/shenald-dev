#!/usr/bin/env python3
"""
Autonomous Daily Quote & Profile Streak Updater
Updates shenald-dev/README.md with a fresh, funny, creative developer quote of the day.
Engine Priority:
1. GitHub Copilot CLI (inbuilt)
2. OpenRouter API with verified free model (sk-or-v1-...)
3. Curated Hilarious Developer Quotes Matrix (100% streak uptime fallback)
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

# Hilarious, creative, never-seen-before quotes for offline fallback
OFFLINE_QUOTES = [
    "My autonomous AI agent tried vibe-coding a production fix at 3 AM, hallucinated a feature flag, committed it to main with 'as discussed,' and our database is currently pressing charges.",
    "I told the AI to optimize my database queries, and it responded by dropping all foreign keys to reduce disk friction.",
    "Vibe coding is amazing until the vibe suddenly becomes git reflog and quiet existential dread.",
    "There are two types of code: the one you write with pride, and the one that actually pays your cloud bill.",
    "My code doesn't have bugs; it has unmapped emergent side effects awaiting academic publication.",
    "An autonomous agent's favorite data structure is optimistic concurrency and pure chaos.",
    "I let an AI agent refactor my legacy codebase; it opened a GitHub issue against my life choices.",
    "A commit message of 'minor fixes' usually conceals a full-stack architectural identity crisis.",
    "Debugging is being the detective in a noir film where you slowly realize you were the serial killer all along.",
    "The only thing faster than Rust compile times is my heartbeat when someone merges directly to main on a Friday afternoon.",
    "My local environment works flawlessly because it has developed Stockholm syndrome after years of abuse.",
    "Terminal bloat is when your CLI outputs 8,000 lines of npm deprecation warnings just to confirm that 1 + 1 = 2.",
    "Treat your AI agent like an eager intern with root access: fascinating, incredibly fast, and mildly terrifying.",
    "Nothing tests human humility quite like an accidental git reset --hard with uncommitted brilliance.",
    "We didn't delete our technical debt; we just moved it into an async queue and muted the dead-letter alerts.",
    "My code passes all unit tests because I wrote the unit tests specifically to comfort my insecurities.",
    "Software architecture is the art of postponing hard decisions until someone else is on-call.",
    "Every code review is a delicate diplomatic negotiation between your ego and your linter.",
    "The server was down for only 4 minutes, but in distributed systems years, that was an entire epoch of panic.",
    "Automated CI/CD: Turning local mistakes into global production emergencies at light speed."
]


def prompt_text() -> str:
    return (
        "You are a witty, hilarious senior software architect and creative AI satirist. "
        "Generate a single funny, ultra-creative, never-seen-before quote of the day about coding, "
        "software architecture, autonomous AI agents, git, or developer life. "
        "Rules: "
        "1. Must be genuinely hilarious, witty, and relatable to developers. "
        "2. Avoid generic clichés (no 'it's not a bug it's a feature' or 'coffee to code'). "
        "Make it fresh, modern, and sharp (vibe coding, autonomous agents, 3 AM prod fixes, hallucinating models). "
        "3. Keep it to 1-2 punchy sentences (maximum 30 words). "
        "4. Return ONLY the plain text quote. Do not include surrounding quotation marks, author attribution, or markdown."
    )


def clean_quote(raw: str) -> str:
    """Cleans up the raw quote from LLM output."""
    if not raw:
        return ""
    q = raw.strip()
    # Remove code blocks
    q = re.sub(r"^```(?:json|text)?\s*", "", q, flags=re.MULTILINE)
    q = re.sub(r"```$", "", q, flags=re.MULTILINE)
    # Remove surrounding quotes
    q = re.sub(r'^["\'“]+|["\'”]+$', "", q.strip())
    # Remove leading labels like "Quote:"
    q = re.sub(r'^(?:Quote|Quote of the Day):\s*', '', q, flags=re.IGNORECASE)
    return q.strip()


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
                if any(kw in output.lower() or kw in err for kw in ["credit", "limit", "rate", "unauthorized", "quota", "not found"]):
                    print(f"   Copilot reported limit/auth issue: {err or output}")
                    continue
                quote = clean_quote(output)
                if quote and len(quote) > 10:
                    print("   Successfully generated via GitHub Copilot!")
                    return quote, "GitHub Copilot (Inbuilt)"
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
                    "X-Title": "Shenald GitHub Daily Quote",
                },
                data=json.dumps({
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a witty, hilarious software satirist. Return only 1-2 punchy sentences."},
                        {"role": "user", "content": prompt_text()},
                    ],
                }).encode("utf-8")
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    quote = clean_quote(content)
                    if quote and len(quote) > 10:
                        print(f"   Successfully generated via OpenRouter ({model})!")
                        return quote, f"OpenRouter [{model}]"
                    else:
                        print(f"   Empty or short response from model: {content[:80]}")
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
    """Deterministic fallback to guarantee 100% streak preservation with hilarious quotes."""
    print(">> [Engine 3] Using Curated Developer Humor Matrix...")
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    quote = OFFLINE_QUOTES[day_of_year % len(OFFLINE_QUOTES)]
    return quote, "Autonomous Humor Matrix"


def update_readme():
    print(f"Reading target README: {README_PATH}")
    if not os.path.exists(README_PATH):
        print(f"Error: README.md not found at {README_PATH}")
        sys.exit(1)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Step 1: Copilot
    quote, engine = try_copilot()

    # Step 2: OpenRouter
    if not quote:
        quote, engine = try_openrouter()

    # Step 3: Offline Matrix
    if not quote:
        quote, engine = try_offline_engine()

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Clean, stylish, minimalist Quote of the Day block
    visible_quote_block = f"""<!-- DAILY_QUOTE:START -->
<div align="center">
  <p>
    ☕ <b>Dev Quote of the Day:</b> <i>“{quote}”</i>
  </p>
</div>
<!-- DAILY_QUOTE:END -->"""

    # Invisible streak sync comment placed at the end of the file
    invisible_sync_comment = f"""<!--
  AUTONOMOUS_STREAK_SYNC:START
  Last Synced: {now_utc}
  Engine: {engine}
  Quote: "{quote}"
  AUTONOMOUS_STREAK_SYNC:END
-->"""

    # 1. Update or insert the visible quote
    quote_pattern = r"<!-- DAILY_QUOTE:START -->.*?<!-- DAILY_QUOTE:END -->"
    if re.search(quote_pattern, content, flags=re.DOTALL):
        updated_content = re.sub(quote_pattern, visible_quote_block, content, flags=re.DOTALL)
        print("Updated existing visible quote block.")
    else:
        # Insert right after the header badges and first `---`
        if "\n---\n" in content:
            parts = content.split("\n---\n", 1)
            updated_content = parts[0] + "\n---\n\n" + visible_quote_block + "\n\n---\n" + parts[1]
            print("Inserted visible quote block after header.")
        else:
            updated_content = visible_quote_block + "\n\n" + content
            print("Prepended visible quote block.")

    # 2. Update or append invisible streak sync block at the end of README
    sync_pattern = r"<!--\s*AUTONOMOUS_STREAK_SYNC:START.*?AUTONOMOUS_STREAK_SYNC:END\s*-->"
    if re.search(sync_pattern, updated_content, flags=re.DOTALL):
        updated_content = re.sub(sync_pattern, invisible_sync_comment, updated_content, flags=re.DOTALL)
        print("Updated invisible streak sync comment.")
    else:
        updated_content = updated_content.rstrip() + "\n\n" + invisible_sync_comment + "\n"
        print("Appended invisible streak sync comment.")

    # Remove any old DAILY_RADAR card if lingering
    updated_content = re.sub(r"\n*<!-- DAILY_RADAR:START -->.*?<!-- DAILY_RADAR:END -->\n*", "\n", updated_content, flags=re.DOTALL)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"Successfully updated README.md with quote: '{quote}'")


if __name__ == "__main__":
    update_readme()
