import json
import sys

from logistics_room import InfraiClient, start_session


if __name__ == "__main__":
    shipment = sys.argv[1] if len(sys.argv) > 1 else "SHP-1001"
    print(json.dumps(start_session(InfraiClient(), shipment, "acme-logistics", "dispatcher-1"), indent=2))
