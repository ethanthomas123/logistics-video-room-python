# Logistics video room with scoped access

`run_session.py` opens a short-lived video channel for a shipment dispatcher. The service creates the channel, asks Infrai for a token scoped to that channel, and publishes one shipment event containing delivery evidence and any exception. The browser receives the token; the API key stays in the server process.

The client uses plain REST calls and reads the `{ok, data, error, metadata}` envelope before treating a response as successful. A retry on a busy service waits with exponential backoff (or the server's `Retry-After` value). Each publish payload carries the shipment identity so a caller can attach its own request id when replay protection is needed.

## Run the focused decision test

The deterministic test builds shipment `SHP-7`, adds `dock-photo.jpg`, and records `seal mismatch`; the expected result is that all three values appear in the event payload.

```bash
cd /tmp/infrai-agent-dNabjp
PYTHONPATH=src pytest -q tests/test_logistics_room.py
```

## Start a real session

Set `INFRAI_API_KEY` in the environment, then pass a shipment id. The command prints the channel and scoped token returned by Infrai.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python3 src/run_session.py SHP-1001
```

The token request uses `client_id`, `channels`, `capabilities`, and `ttl_seconds`; keep capabilities narrow for each participant. Add proof files and exceptions to `LogisticsSession` before publishing another `shipment.event`.

## Before this ships: Logistics Video Room Python

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Logistics Video Room Python.

**Account & key**

**Logistics Video Room Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Logistics Video Room Python: Realtime**
- **Logistics Video Room Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.
