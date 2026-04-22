# YieldClaw — Standing Orders
**Project:** Hyperliquid BTC Grid Bot (Testnet Phase)
**Created:** 2026-04-22
**Status:** DEPLOYED (awaiting testnet key + first fills)

---

## Mission

Deploy a conservative BTC-USDC grid bot on Hyperliquid testnet. Prove the plumbing works. No AI, no complex logic — just a working grid that fills orders and logs cleanly.

---

## Architecture

```
Mac Mini 24GB (192.168.0.104)
├── ~/projects/yieldclaw/     # Bot code (cloned from chainstacklabs)
│   ├── bots/btc_conservative.yaml  # Strategy config
│   ├── src/                  # Bot source
│   └── .venv/                # Python env (uv)
└── ~/projects/yieldclaw/.env # Private key (gitignored)
```

---

## Deployment Steps Completed (2026-04-22)

- [x] Cloned https://github.com/chainstacklabs/hyperliquid-trading-bot
- [x] Synced dependencies via `uv sync` on Mac Mini 24GB
- [x] Validated bot config syntax

---

## Pending: Testnet Key + First Fills

### 1. Set Private Key

On Mac Mini 24GB, create `.env` file:

```bash
ssh -i ~/.ssh/id_ed25519 winstonsmacmini2@192.168.0.104

# Create .env with testnet private key
cat > ~/projects/yieldclaw/.env << 'EOF'
HYPERLIQUID_TESTNET_PRIVATE_KEY=YOUR_KEY_HERE
HYPERLIQUID_TESTNET=true
EOF
```

Eddie: You need to provide the Hyperliquid testnet private key from https://testnet.hyperliquid.xyz

### 2. Get Testnet Funds

1. Go to https://testnet.hyperliquid.xyz
2. Sign in with wallet
3. Get testnet BTC from https://faucet.chainstack.com/hyperliquid-testnet-faucet
4. Need ~0.01 BTC minimum for 10-level grid

### 3. Run Bot

```bash
ssh -i ~/.ssh/id_ed25519 winstonsmacmini2@192.168.0.104

source $HOME/.local/bin/env
cd ~/projects/yieldclaw

# Validate config
uv run python src/run_bot.py --validate

# Run bot
uv run python src/run_bot.py bots/btc_conservative.yaml
```

### 4. Verify Fills

Look for logs like:
- `📋 Grid orders placed: 10 levels`
- `💰 Order filled: BUY @ 95000.00`
- `💰 Order filled: SELL @ 105000.00`

---

## Grid Parameters (Conservative — Testnet)

| Parameter | Value |
|-----------|-------|
| Symbol | BTC-USDC |
| Levels | 10 |
| Price Range | ±5% (auto) |
| Max Allocation | 10% of account |
| Rebalance Trigger | 12% price move |
| Max Drawdown | 15% |

---

## Phase 2: Cyclone Integration (Week 2-3)

### Cyclone Score → Grid Mode Script

```
projects/yieldclaw/cyclone_grid_switcher.py
```

Logic:
- Score ≥ 70 → SHORT grid mode (aggressive, ±6% range)
- Score 40-70 → NEUTRAL grid mode (±4% range)
- Score < 40 → GRID OFF, all capital to USDC

### Cyclone Output

Katie: Output score to `/tmp/cyclone_score.txt` every 4 hours:
```
SCORE=65
MODE=NEUTRAL
TIMESTAMP=2026-04-22T16:00:00Z
```

---

## Phase 3: Full Integration (Week 3-4)

- Sam: Daily grid performance briefing (via Sam morning report)
- Winston: Telegram alerts on fills + kill switch events
- Kill switch: 10% max drawdown stops all trading

---

## File Structure

```
projects/yieldclaw/
├── bots/
│   └── btc_conservative.yaml  # Neutral mode config
├── src/
│   ├── run_bot.py              # Entry point
│   ├── core/
│   │   ├── engine.py           # Trading engine
│   │   ├── key_manager.py      # API key handling
│   │   └── risk_manager.py      # Risk controls
│   └── exchanges/
│       └── hyperliquid.py      # Hyperliquid adapter
├── cyclone_grid_switcher.py   # [Phase 2] Score-based mode switcher
├── STANDING_ORDERS.md          # This file
└── .env                        # Private keys (NOT committed)
```

---

## Git Commit

Bot code committed to `projects/yieldclaw/` on Winston's workspace.
Commit: `feat(yieldclaw): initial Chainstack grid bot clone — 2026-04-22`

---

## Notes

- Bot uses Hyperliquid testnet API: `https://api.hyperliquid-testnet.xyz`
- All trades are simulated — no real funds
- Private keys stored in `.env` on Mac Mini only — never in git
- Bot can run headless via `nohup` or background session