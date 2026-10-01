from logistics_room import LogisticsSession, ProofOfDelivery, ShipmentEvent


def test_exception_and_proof_are_in_published_payload():
    session = LogisticsSession("SHP-7", "acct-1", "shipment-SHP-7")
    session.add_event(ShipmentEvent("arrived", "2026-09-07T09:00:00Z"))
    session.add_proof(ProofOfDelivery("dock-photo.jpg", "image/jpeg"))
    session.flag_exception("seal mismatch")
    payload = session.event_payload()
    assert payload["events"][0]["kind"] == "arrived"
    assert payload["proof_files"][0]["name"] == "dock-photo.jpg"
    assert payload["exceptions"] == ["seal mismatch"]
