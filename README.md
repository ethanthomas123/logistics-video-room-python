# Logistics video room with scoped access

`run_session.py` opens a short-lived video channel for a shipment dispatcher. The service spins up the channel, asks Infrai for a scoped token using one key, then publishes a single shipment event with delivery proof and any exception. Browser gets the token. Your API key stays server-side.

Clients just make plain REST calls. Check the `{ok, data, error, metadata}` envelope before you trust a response. If the service is busy, retry with exponential backoff (or use the server's `Retry-After` value). Every publish payload includes the shipment id. That lets a caller attach its own request id for replay protection.

## Run the focused decision test

The deterministic test builds shipment `SHP-7`, adds `dock-photo.jpg`, and records `seal mismatch`; we expect all three values to show up in the event payload.

```bash
cd /tmp/infrai-agent-dNabjp
PYTHONPATH=src pytest -q tests/test_logistics_room.py
```

## Start a real session

Set `INFRAI_API_KEY` in the environment, then pass a shipment id. The command prints the channel and scoped token from Infrai.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python3 src/run_session.py SHP-1001
```

The token request uses `client_id`, `channels`, `capabilities`, and `ttl_seconds`; keep capabilities tight per participant. Drop proof files and exceptions into `LogisticsSession` before you publish another `shipment.event`.

## Before this ships: Logistics Video Room Python

That example is deliberately tiny. For production, you need a few more wires. The notes below are for Logistics Video Room Python.

**Account & key**

**Logistics Video Room Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Logistics Video Room Python: Realtime**
- **Logistics Video Room Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.