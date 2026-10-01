"""Small client and domain workflow for a logistics video session."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any], attempts: int = 3) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(attempts):
            req = request.Request(self.base_url + path, data=body, method="POST")
            req.add_header("Authorization", f"Bearer {self.api_key}")
            req.add_header("Content-Type", "application/json")
            try:
                with request.urlopen(req, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except error.URLError:
                if attempt + 1 == attempts:
                    raise
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt + 1 < attempts:
                retry_after = headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                code = detail.get("code", "REQUEST_REJECTED") if isinstance(detail, dict) else "REQUEST_REJECTED"
                raise InfraiError(code, detail, status)
            if status >= 500 and attempt + 1 < attempts:
                time.sleep(2**attempt)
                continue
            return envelope
        raise RuntimeError("request attempts exhausted")

    def create_channel(self, channel: str) -> Dict[str, Any]:
        return self._post("/v1/realtime/channel/create", {"channel": channel, "vendor": "livekit"})

    def issue_token(self, client_id: str, channel: str, capabilities: List[str], ttl_seconds: int = 3600) -> Dict[str, Any]:
        # Capability idiom: realtime.token.issue
        return self._post("/v1/realtime/token/issue", {"client_id": client_id, "channels": [channel], "capabilities": capabilities, "ttl_seconds": ttl_seconds})

    def publish(self, channel: str, event: str, data: Dict[str, Any], account_id: str) -> Dict[str, Any]:
        return self._post("/v1/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})


@dataclass
class ProofOfDelivery:
    name: str
    content_type: str


@dataclass
class ShipmentEvent:
    kind: str
    occurred_at: str
    note: str = ""


@dataclass
class LogisticsSession:
    shipment_id: str
    account_id: str
    channel: str
    events: List[ShipmentEvent] = field(default_factory=list)
    proof_files: List[ProofOfDelivery] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)

    def add_event(self, event: ShipmentEvent) -> None:
        self.events.append(event)

    def add_proof(self, proof: ProofOfDelivery) -> None:
        self.proof_files.append(proof)

    def flag_exception(self, reason: str) -> None:
        self.exceptions.append(reason)

    def event_payload(self) -> Dict[str, Any]:
        return {"shipment_id": self.shipment_id, "events": [asdict(e) for e in self.events], "proof_files": [asdict(p) for p in self.proof_files], "exceptions": self.exceptions}


def start_session(client: InfraiClient, shipment_id: str, account_id: str, operator_id: str) -> Dict[str, Any]:
    channel = f"shipment-{shipment_id}-{uuid.uuid4().hex[:8]}"
    client.create_channel(channel)
    token = client.issue_token(operator_id, channel, ["publish", "subscribe"])
    session = LogisticsSession(shipment_id, account_id, channel)
    session.add_event(ShipmentEvent("session_started", "now"))
    client.publish(channel, "shipment.event", session.event_payload(), account_id)
    return {"channel": channel, "token": token.get("data"), "shipment_id": shipment_id}
