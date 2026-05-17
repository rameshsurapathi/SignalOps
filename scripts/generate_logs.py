import os
import random
import datetime

services = {
    "payment-service": {
        "errors": [
            "[WARN] Heap memory at 95%",
            "[ERROR] java.lang.OutOfMemoryError: Java heap space",
            "[FATAL] Application crashing"
        ]
    },
    "auth-service": {
        "errors": [
            "[WARN] Database connection acquisition taking longer than 2000ms",
            "[ERROR] OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections",
            "[FATAL] Service timeout. Liveness endpoint returning 500"
        ]
    },
    "inventory-service": {
        "errors": [
            "[WARN] Retrying connection to warehouse API (attempt 1/3)",
            "[ERROR] java.net.SocketTimeoutException: connect timed out to warehouse.internal.api:443",
            "[FATAL] Unable to reach upstream dependencies. Failing health checks."
        ]
    },
    "api-gateway": {
        "errors": [
            "[WARN] Canary routing anomaly detected",
            "[ERROR] upstream connect error or disconnect/reset before headers. reset reason: connection failure",
            "[ERROR] HTTP 503 Service Unavailable returned to client"
        ]
    },
    "user-service": {
        "errors": [
            "[WARN] Secret mount path not found",
            "[ERROR] Init container failed to read user-db-credentials",
            "[FATAL] Pod startup aborted due to missing configuration"
        ]
    }
}

base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "logs")
os.makedirs(base_dir, exist_ok=True)

for service, config in services.items():
    filepath = os.path.join(base_dir, f"{service}.log")
    with open(filepath, "w") as f:
        # Generate 1000 lines of noise
        for i in range(1000):
            timestamp = datetime.datetime.now() - datetime.timedelta(seconds=1000-i)
            ts_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            f.write(f"{ts_str} [INFO] {service} - Handling standard request. Latency {random.randint(10, 50)}ms\n")
            if random.random() < 0.1:
                f.write(f"{ts_str} [DEBUG] {service} - Cache miss for key {random.randint(1000, 9999)}\n")
        
        # Insert the critical errors at the end
        timestamp = datetime.datetime.now()
        ts_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        for err in config["errors"]:
            f.write(f"{ts_str} {err}\n")

print(f"Generated large simulated log files in {base_dir}")
