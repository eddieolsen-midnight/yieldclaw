#!/usr/bin/env python3
"""
Cyclone Grid Mode Switcher

Reads Cyclone v2 score from shared file and calls Hummingbot API
to switch grid mode on Mac Mini 24GB.

Score → Mode mapping:
  ≥70: SHORT grid (aggressive, ±6% range)
  40-69: NEUTRAL grid (±4% range)
  <40: GRID OFF, all capital to USDC

Usage:
  python cyclone_grid_switcher.py

Runs continuously, checking score every 60 seconds.
Logs all mode changes.
"""

import os
import time
import httpx
from pathlib import Path

# Configuration
SCORE_FILE = "/tmp/cyclone_score.txt"
HUMMINGBOT_API = "http://localhost:8501"  # Hummingbot gateway port
LOG_FILE = "/tmp/grid_mode_switcher.log"

# Grid parameters by mode
GRID_PARAMS = {
    "SHORT": {
        "levels": 10,
        "range_pct": 6.0,  # ±6% in short mode
        "mode": "short_grid",
    },
    "NEUTRAL": {
        "levels": 10,
        "range_pct": 4.0,  # ±4% in neutral mode
        "mode": "neutral_grid",
    },
    "OFF": {
        "levels": 0,
        "range_pct": 0.0,
        "mode": "grid_off",
    },
}

# Kill switch thresholds
MAX_DRAWDOWN_PCT = 10.0
MAX_POSITION_PCT = 15.0


def log(msg: str) -> None:
    """Write log message to file and stdout"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def read_cyclone_score() -> tuple[int | None, str | None]:
    """Read score and mode from Cyclone output file"""
    score_file = Path(SCORE_FILE)
    if not score_file.exists():
        return None, None

    try:
        content = score_file.read_text().strip()
        score = None
        mode = None

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("SCORE="):
                score = int(line.split("=")[1])
            elif line.startswith("MODE="):
                mode = line.split("=")[1]

        return score, mode
    except Exception as e:
        log(f"⚠️ Error reading score file: {e}")
        return None, None


def determine_mode(score: int) -> str:
    """Map score to grid mode"""
    if score >= 70:
        return "SHORT"
    elif score >= 40:
        return "NEUTRAL"
    else:
        return "OFF"


def call_hummingbot_mode(mode: str) -> bool:
    """Call Hummingbot API to switch grid mode"""
    params = GRID_PARAMS[mode]

    try:
        response = httpx.post(
            f"{HUMMINGBOT_API}/api/v1/grid/mode",
            json={
                "mode": params["mode"],
                "levels": params["levels"],
                "range_pct": params["range_pct"],
                "symbol": "BTC",
            },
            timeout=10.0,
        )

        if response.status_code == 200:
            log(f"✅ Hummingbot mode switched to {mode}")
            return True
        else:
            log(f"❌ Hummingbot API error: {response.status_code} — {response.text}")
            return False

    except httpx.ConnectError:
        log("⚠️ Cannot connect to Hummingbot API (is it running?)")
        return False
    except Exception as e:
        log(f"⚠️ Hummingbot API error: {e}")
        return False


def main():
    """Main loop — check score every 60 seconds"""
    log("🚀 Cyclone Grid Switcher started")
    last_mode = None

    while True:
        score, cyclone_mode = read_cyclone_score()

        if score is None:
            log("⏳ No Cyclone score found, waiting...")
            time.sleep(60)
            continue

        new_mode = determine_mode(score)

        if new_mode != last_mode:
            log(f"📊 Cyclone score: {score} → Mode: {new_mode}")

            success = call_hummingbot_mode(new_mode)
            if success:
                last_mode = new_mode
            else:
                log(f"⚠️ Mode switch to {new_mode} failed, retrying in 60s")
        else:
            log(f"📊 Score {score} → Mode {new_mode} (no change)")

        time.sleep(60)


if __name__ == "__main__":
    main()