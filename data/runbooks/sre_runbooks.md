# 🛡️ SignalOps Corporate Runbook Repository

This knowledge base contains approved remediation procedures for the SignalOps microservices ecosystem.

---

## 🚀 payment-service: OOMKill Remediation
**Incident Pattern:** Container terminates with exit code 137.
**Root Cause:** Memory limit (ResourceQuota) exceeded during peak transaction processing.
**Approved Fix:** 
1. Patch the K8s deployment to increase `limits.memory` to `512Mi`.
2. Ensure `Xmx` values are adjusted if the service is JVM-based.
3. Restart pods to apply changes.

---

## 🔐 auth-service: DB Timeout Remediation
**Incident Pattern:** 503 errors and "Connection Pool Exhausted" log entries.
**Root Cause:** DB connection leak or slow queries locking the pool.
**Approved Fix:**
1. Flush the service connection pool via management endpoint.
2. Scale auth-service to 3 replicas to distribute connection load.
3. Check `max_connections` on the Postgres instance.

---

## 📦 inventory-service: Network Partition
**Incident Pattern:** "Unknown Host" or "Connection Timeout" when calling upstream.
**Root Cause:** CoreDNS staleness or failing proxy nodes in the VPC.
**Approved Fix:**
1. Force CoreDNS rollout to clear cache.
2. Update service mesh rules to bypass the identified failing node.

---

## 🌐 api-gateway: High Error Rate
**Incident Pattern:** HTTP 500 spike immediately following a CI/CD rollout.
**Root Cause:** Incompatible canary deployment or bad configuration values.
**Approved Fix:**
1. Immediate rollback to the previous stable image tag.
2. Verify ingress controller logs for header mismatch.

---

## 👤 user-service: Bad Configuration
**Incident Pattern:** CreateContainerConfigError or "Secret Not Found".
**Root Cause:** Missing or deleted K8s Secrets/ConfigMaps.
**Approved Fix:**
1. Re-create the missing 'db-credentials' secret from Vault.
2. Trigger a rolling update to the user-service.
