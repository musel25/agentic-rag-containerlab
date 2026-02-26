import json
from typing import List
# (Assume your Pydantic classes are imported here)

def generate_srl_telemetry_config(intent: IntentSkeleton, resolved_paths: List[str]) -> dict:
    """
    Translates an IntentSkeleton into an SR Linux telemetry JSON configuration.
    """
    # Create unique identifiers based on the intent
    target_name = intent.target_router.address or "default-router"
    collector_group_name = f"cg-{intent.collector.address}"
    sensor_group_name = f"sg-{target_name}-sensors"
    sub_name = f"sub-{target_name}-telemetry"

    # 1. Build the Destination Group
    destination_group = {
        "name": collector_group_name,
        "destination": [
            {
                "host": intent.collector.address,
                "port": intent.collector.port
            }
        ]
    }

    # 2. Build the Sensor Group using the resolved paths
    sensor_group = {
        "name": sensor_group_name,
        "sensor": [{"path": path} for path in resolved_paths]
    }

    # 3. Build the Subscription linking the two
    subscription = {
        "name": sub_name,
        "destination-group": [collector_group_name],
        "sensor-group": [
            {
                "name": sensor_group_name,
                "sample-interval": intent.sample_interval_ms or 10000
            }
        ]
    }

    # Assemble the final SR Linux config payload
    srl_config = {
        "system": {
            "telemetry": {
                "destination-group": [destination_group],
                "sensor-group": [sensor_group],
                "subscription": [subscription]
            }
        }
    }

    return srl_config

# --- Execution Example ---

# 1. Mocking the parsed intent (similar to Test 2 from your previous list)
mock_intent_data = {
    "device_hints": {"vendor": "nokia", "nos": "sr-linux"},
    "target_router": {"address": "srl-router", "port": 57400},
    "collector": {"address": "10.0.0.5", "port": 50000},
    "telemetry_goal": ["system_cpu", "system_memory"],
    "sample_interval_ms": 2000,
    "telemetry_mode": "dial-out",
    "protocol": "grpc"
}

intent = IntentSkeleton(**mock_intent_data)

# 2. Mocking the resolved YANG paths
resolved_paths = [
    "/platform/control[name=cpm1]/cpu/utilization",
    "/platform/control[name=cpm1]/memory"
]

# 3. Generate the payload
config_payload = generate_srl_telemetry_config(intent, resolved_paths)

print(json.dumps(config_payload, indent=2))