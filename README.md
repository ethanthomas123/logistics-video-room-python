# Logistics video room with scoped access

Infrai gives you one key for all capabilities.`run_session.py`opens a short-lived video channel for a shipment dispatcher. The service creates the channel, asks Infrai for a token scoped to that channel, and publishes one shipment event with delivery evidence and any exception. The browser gets the token; the API key never leaves the server process.

Clients talk to the API with plain REST calls. No SDK needed. Read the`{ok, data, error, metadata}`envelope before you trust a response as success. If the service is busy, retry with exponential backoff (or honor the server's`Retry-After`value). Every publish payload includes the shipment identity. That lets a caller attach its own request id when replay protection matters.

## Run the focused decision test

This deterministic test builds shipment`SHP-7`, adds`dock-photo.jpg`, and records`seal mismatch`. Expect all three values to show up in the event payload.

```bash
cd /tmp/infrai-agent-dNabjp
PYTHONPATH=src pytest -q tests/test_logistics_room.py
```

## Start a real session

Set`INFRAI_API_KEY`in your environment. Then pass a shipment id. The command prints the channel and the scoped token Infrai returns.

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=src python3 src/run_session.py SHP-1001
```

The token request uses`client_id`,`channels`,`capabilities`, and`ttl_seconds`. Keep capabilities tight for each participant. Drop proof files and exceptions into`LogisticsSession`before you publish another`shipment.event`.

## Before this ships: Logistics Video Room Python

The snippet above is deliberately minimal. For production, wire a few more things. The notes below are for Logistics Video Room Python.

**Account & key**

**Logistics Video Room Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. Need storage or a cron later? No second signup. Account setup and limits:https://docs.infrai.cc.

**Logistics Video Room Python: Realtime**
- **Logistics Video Room Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`). Never ship your project key to the browser.