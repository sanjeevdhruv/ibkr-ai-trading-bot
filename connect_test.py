"""Minimal IBKR connection test (paper trading).

WARNING: This project defaults to PAPER trading (TWS port 7497 / Gateway 4002).
Do not point it at a live port (7496 / 4001). The script refuses to run if the
port in settings.json is not on the paper allow-list.

Usage:
    python connect_test.py
"""
import json
import sys
from pathlib import Path

try:
    from ib_async import IB, Stock  # maintained fork of ib_insync
except ImportError:
    from ib_insync import IB, Stock

PAPER_PORTS = {7497, 4002}


def load_settings(path: str = "settings.json") -> dict:
    return json.loads(Path(path).read_text())


def main() -> int:
    settings = load_settings()
    cfg = settings["ibkr"]
    port = int(cfg["port"])

    if port not in PAPER_PORTS or settings["environment"].get("mode") != "paper":
        print(f"REFUSING: port {port} / mode '{settings['environment'].get('mode')}' is not paper trading.")
        return 1

    ib = IB()
    print(f"Connecting to {cfg['host']}:{port} (clientId={cfg['client_id']}) ...")
    try:
        ib.connect(cfg["host"], port, clientId=int(cfg["client_id"]),
                   readonly=bool(cfg.get("readonly", True)),
                   timeout=float(cfg.get("timeout_sec", 10)))
    except Exception as e:
        print(f"Connection failed: {e!r}")
        print("Check: TWS/Gateway is running and logged in to PAPER, API socket clients are enabled,"
              " the port matches, and 127.0.0.1 is a trusted IP.")
        return 1

    try:
        accounts = ib.managedAccounts()
        print(f"Connected. Server version {ib.client.serverVersion()}, accounts: {accounts}")
        # Paper account IDs start with "DU" (or "DF"); live ones start with "U".
        # The socket port alone does not prove paper: TWS can serve a live login on 7497.
        if not accounts or not all(a.startswith("D") for a in accounts):
            print(f"REFUSING: {accounts} does not look like a paper account. "
                  "Log out of TWS and log back in with your PAPER trading login.")
            return 1

        summary = {v.tag: v.value for v in ib.accountSummary()
                   if v.tag in ("NetLiquidation", "AvailableFunds", "BuyingPower")}
        print(f"Account summary: {json.dumps(summary)}")

        # Delayed data works without market-data subscriptions (type 3).
        ib.reqMarketDataType(3)
        spy = Stock("SPY", "SMART", "USD")
        ib.qualifyContracts(spy)
        ticker = ib.reqMktData(spy, "", snapshot=True)
        ib.sleep(3)
        print(f"SPY snapshot: last={ticker.last} bid={ticker.bid} ask={ticker.ask} close={ticker.close}")
        print("OK: Python <-> IBKR paper connection works.")
        return 0
    finally:
        ib.disconnect()


if __name__ == "__main__":
    sys.exit(main())
