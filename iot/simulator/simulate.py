"""
Lightweight IoT simulation stub for AgriTwin MVP.
Uses POST /iot/simulate so readings are always source_type=simulation.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def post_simulate(api_url: str, token: str, farm_id: int, scenario: str) -> None:
    payload = {"farm_id": farm_id, "scenario": scenario}
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/iot/simulate",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        print(resp.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="AgriTwin IoT simulator")
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--token", required=True)
    parser.add_argument("--farm-id", type=int, required=True)
    parser.add_argument("--scenario", default="drought_risk")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=30)
    args = parser.parse_args()

    while True:
        try:
            post_simulate(args.api, args.token, args.farm_id, args.scenario)
            print(f"[simulation] posted scenario={args.scenario}")
        except urllib.error.URLError as exc:
            print(f"[simulation] error: {exc}")
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
