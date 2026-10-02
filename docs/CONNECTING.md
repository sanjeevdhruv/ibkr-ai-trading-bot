# Connecting IBKR, Python and Claude

> **Paper trading only.** Everything here targets the paper port (TWS `7497`, IB Gateway `4002`).
> Do not switch to a live port (`7496` / `4001`) until the strategy and the risk layer have been
> reviewed and tested for weeks on paper.

The bot, TWS and Python all run **on your own computer**. TWS only listens on `127.0.0.1`,
so nothing in the cloud (including a cloud Claude session) can reach it directly.

```
 Claude Code (your terminal) ──edits/runs──▶ Python bot ──socket 127.0.0.1:7497──▶ TWS / IB Gateway (paper) ──▶ IBKR
                                              │
                                              └──(optional) HTTPS──▶ Anthropic API
```

## 1. TWS / IB Gateway API settings

In TWS: **File → Global Configuration → API → Settings** (Gateway: **Configure → Settings → API → Settings**).

| Setting | Value |
|---|---|
| Enable ActiveX and Socket Clients | ✅ on |
| Socket port | `7497` (TWS paper) or `4002` (Gateway paper) |
| Read-Only API | ✅ on for the first test; turn off only when you are ready to place paper orders |
| Allow connections from localhost only | ✅ on |
| Trusted IPs | `127.0.0.1` |
| Master API client ID | leave blank |

Log in with your **paper** credentials (paper account IDs start with `D`). Click Apply/OK.

## 2. Python environment

Python 3.10+ recommended.

```bash
git clone https://github.com/sanjeevdhruv/ibkr-ai-trading-bot.git
cd ibkr-ai-trading-bot
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r req.txt
pip install ib_async               # maintained successor to ib_insync (same API)
```

`ib_insync` is no longer maintained; `ib_async` is the drop-in fork. `connect_test.py` uses
`ib_async` if installed and falls back to `ib_insync`.

## 3. Run the connection test

With TWS running and logged in to paper:

```bash
python connect_test.py
```

Expected output:

```
Connecting to 127.0.0.1:7497 (clientId=10) ...
Connected. Server version 176, accounts: ['DU1234567']
Account summary: {"NetLiquidation": "1000000.00", ...}
SPY snapshot: last=... bid=... ask=... close=...
OK: Python <-> IBKR paper connection works.
```

Connection settings live in `settings.json`. The script refuses to run against any port that
is not on the paper allow-list.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `ConnectionRefusedError` | TWS not running, API not enabled, or wrong port (7497 vs 4002). |
| Connects then times out / hangs | A pop-up in TWS is asking to accept the incoming connection. Accept it, or add `127.0.0.1` to Trusted IPs. |
| `clientId already in use` | Another script is connected with the same ID. Change `client_id` in `settings.json`; every script needs its own. |
| SPY prices are `nan` | No market-data subscription and delayed data not yet returned. Re-run, or check market hours. Delayed data (type 3) is requested by default. |
| Account ID does not start with `D` | You are logged in to live. Log out and use the paper login. |

## 4. Connecting Claude

There are two separate, independent pieces.

### a) Claude Code: Claude as your developer

Claude Code runs in your terminal, inside this repo, on the same machine as TWS. It can read and
edit the bot's code and run `python connect_test.py` against your local TWS.

```bash
npm install -g @anthropic-ai/claude-code
cd ibkr-ai-trading-bot
claude
```

Then ask it things like "run connect_test.py and fix any errors". It asks permission before
running commands. Claude in the cloud (this project) writes and pushes code to GitHub; you
`git pull` locally and run it.

### b) Anthropic API: Claude inside the bot (optional)

Only needed if the bot itself should ask Claude for an opinion at runtime (e.g. to review a
scanner shortlist). Get a key at https://console.anthropic.com, put it in `.env` (git-ignored):

```
ANTHROPIC_API_KEY=sk-ant-...
```

```bash
pip install anthropic python-dotenv
```

```python
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=500,
    messages=[{"role": "user", "content": 'Reply with strict JSON {"ok": true}'}],
)
print(msg.content[0].text)
```

Claude's output should only ever be **advice** fed into the deterministic risk layer. It must
never place orders directly or bypass position-size and per-trade risk limits.

## Next steps

Once `connect_test.py` passes: `scanner.py` (gappers), `rules.json`, a separate risk layer,
`execution.py` (bracket orders), `brain.py` (30-minute loop) and `alerts.py`.
