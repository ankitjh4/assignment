# Observability Plan - DRINKOO RAG Chatbot

**Date:** 2026-06-14  
**Version:** 1.0

## Overview

This document outlines the observability strategy for DRINKOO, covering:

- Health and status monitoring
- Logging strategy
- Metrics collection
- Alerting rules
- Production monitoring plan

---

## 1. Health Check Endpoints

### `/health` Endpoint

**Purpose:** Quick API health status check

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-06-14T10:00:00Z",
  "api_version": "1.0.0",
  "environment": "development",
  "database": {
    "status": "healthy",
    "message": "Database ready (8 tables)",
    "tables_count": 8,
    "can_read": true,
    "can_write": true
  },
  "rag_ready": true
}
```

**Check Frequency:** Every 30 seconds (recommended)

**Healthy Criteria:**

- Database connectivity: OK
- All 8 tables present
- Read and write capabilities confirmed
- RAG API key configured

---

### `/status` Endpoint

**Purpose:** Detailed status information (requires optional auth)

**Response:**

```json
{
  "api_health": "healthy",
  "database_health": {
    "status": "healthy",
    "message": "Database ready (8 tables)",
    "tables_count": 8,
    "can_read": true,
    "can_write": true
  },
  "rag_ready": true,
  "timestamp": "2026-06-14T10:00:00Z"
}
```

**Check Frequency:** On demand or every 60 seconds

---

## 2. Logging Strategy

### Log Levels

| Level    | Usage                      | Example                                         |
| -------- | -------------------------- | ----------------------------------------------- |
| DEBUG    | Development details        | "Token decoded: user_id=123"                    |
| INFO     | Normal operations          | "User logged in: alice (ID: 5)"                 |
| WARNING  | Unexpected but recoverable | "Login failed: invalid password (alice)"        |
| ERROR    | Errors requiring attention | "Database connection error: connection refused" |
| CRITICAL | System failures            | "OpenRouter API unavailable"                    |

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
2026-06-14 10:00:00,123 - backend.auth - INFO - User logged in: alice (ID: 5)
```

### Logged Events

#### Authentication

✅ User signup
✅ User login (success)
⚠️ Login failure (invalid password)
⚠️ Login failure (user not found)
✅ Token creation
⚠️ Token verification failure
⚠️ Duplicate user attempt

#### Chatbot Operations

✅ Query received
✅ Documents retrieved (count)
✅ LLM response generated
⚠️ No relevant documents found
⚠️ LLM API error
⚠️ Query processing timeout

#### File Upload

✅ File uploaded (filename, size)
⚠️ Invalid MIME type rejected
⚠️ File too large rejected
⚠️ Upload directory creation failed

#### Database

✅ Connection established
⚠️ Query execution error
⚠️ Database locked
⚠️ Foreign key constraint violation
⚠️ Health check failed

#### API

✅ Startup initialized
⚠️ Configuration validation failed
⚠️ CORS error
⚠️ 401 Unauthorized
⚠️ 500 Server error
✅ Shutdown complete

### Log Storage

**Development:**

- File: `logs/drinkoo.log`
- Max Size: 10MB per file
- Backup Count: 5 files
- Format: Rotating file handler

**Production (Recommended):**

- Centralized logging service (ELK Stack, Splunk, Datadog)
- Retention: 30-90 days
- Real-time alerting on ERROR/CRITICAL

---

## 3. Metrics to Monitor

### System Metrics

| Metric                  | Target  | Check Frequency |
| ----------------------- | ------- | --------------- |
| API Response Time (p50) | <100ms  | Per request     |
| API Response Time (p95) | <500ms  | Per request     |
| API Response Time (p99) | <1000ms | Per request     |
| Error Rate              | <1%     | Per minute      |
| Database Latency (p50)  | <10ms   | Per query       |
| Database Latency (p95)  | <50ms   | Per query       |

### Application Metrics

| Metric           | Description                 |
| ---------------- | --------------------------- |
| Total Requests   | Cumulative API calls        |
| Failed Requests  | Count of 4xx/5xx responses  |
| Auth Failures    | Login/signup rejections     |
| Chatbot Queries  | Total RAG queries processed |
| Upload Successes | Completed file uploads      |
| Upload Failures  | Rejected uploads            |

### RAG Metrics

| Metric                   | Target | Description                       |
| ------------------------ | ------ | --------------------------------- |
| Query Processing Time    | <2s    | Time from query to response       |
| Document Retrieval Count | 3+     | Articles/products retrieved       |
| LLM Response Time        | <1s    | Time for LLM API call             |
| Context Relevance        | >0.7   | Relevance score                   |
| Hallucination Rate       | <5%    | % of responses with made-up facts |

### Database Metrics

| Metric                      | Target                            |
| --------------------------- | --------------------------------- |
| Table Row Counts            | Stable or growing (not shrinking) |
| Index Hit Ratio             | >90%                              |
| Connection Pool Utilization | <80%                              |
| Foreign Key Violations      | 0                                 |

---

## 4. Alerting Rules

### Critical Alerts (Page On-Call)

| Alert           | Condition                   | Action                |
| --------------- | --------------------------- | --------------------- |
| API Down        | Health check fails >2 times | Page on-call engineer |
| Database Down   | Cannot connect to DB        | Page on-call engineer |
| Error Rate High | >5% failed requests (5 min) | Page on-call engineer |
| LLM API Failure | OpenRouter API returns 5xx  | Page on-call engineer |
| Disk Full       | <1GB free space             | Page on-call engineer |

### High Priority Alerts (Email)

| Alert                 | Condition                         |
| --------------------- | --------------------------------- |
| High Latency          | p95 response time >500ms (10 min) |
| Auth Failures Spike   | >10 failed logins in 5 min        |
| Database Slow Queries | Query >1s (3+ times in 5 min)     |
| High Memory Usage     | >80% utilization (sustained)      |
| Many Failed Uploads   | >20% upload rejection rate        |

### Low Priority Alerts (Logging)

| Alert                  | Condition                  |
| ---------------------- | -------------------------- |
| Low Disk Space Warning | <10GB free (non-critical)  |
| Deprecated API Usage   | Usage of old endpoints     |
| Configuration Warning  | Non-standard config values |

---

## 5. Dashboard Recommendations

### Real-Time Dashboard (Production)

**Displays:**

1. API Health Status (green/yellow/red)
2. Database Health Status
3. Request rate (requests/sec)
4. Error rate (%)
5. Average response time
6. Active connections
7. Recent errors log
8. RAG query success rate

**Refresh Rate:** 5-10 seconds

### SLA Dashboard

| Metric              | SLA Target | Current |
| ------------------- | ---------- | ------- |
| Availability        | 99.9%      | TBD     |
| Response Time (p50) | <100ms     | TBD     |
| Response Time (p95) | <500ms     | TBD     |
| Error Rate          | <1%        | TBD     |

---

## 6. Production Monitoring Setup

### Infrastructure Monitoring

```bash
# CPU, Memory, Disk
- Monitor: All resources
- Tool: Prometheus/Grafana or CloudWatch
- Alerts: >80% utilization

# Network I/O
- Monitor: Bandwidth usage
- Tool: Network monitoring tools
- Alerts: >80% capacity

# Disk I/O
- Monitor: Read/write latency
- Tool: iostat or cloud provider tools
- Alerts: >100ms latency
```

### Application Monitoring

```bash
# APM (Application Performance Monitoring)
Tool: Datadog, New Relic, Dynatrace
Tracks:
  - Request tracing
  - Error tracking
  - Performance profiling
  - Dependency mapping
```

### Log Aggregation

```bash
# ELK Stack / Splunk / Datadog Logs
Store: Centralized log service
Retention: 30-90 days
Search: Full-text search enabled
Alerts: On ERROR/CRITICAL keywords
```

---

## 7. Rollback Procedure

### Immediate Rollback (If High Severity Issue)

1. **Stop Current Deployment**

   ```bash
   sudo systemctl stop drinkoo
   ```

2. **Identify Last Good Commit**

   ```bash
   git log --oneline | head -10
   git show <good_commit_hash>
   ```

3. **Checkout Previous Version**

   ```bash
   git checkout <good_commit_hash>
   ```

4. **Restart Service**

   ```bash
   sudo systemctl start drinkoo
   ```

5. **Verify Health**

   ```bash
   curl http://localhost:8000/health
   ```

6. **Monitor Logs**
   ```bash
   tail -f logs/drinkoo.log
   ```

### Database Rollback (If Data Issue)

1. **Backup Current State**

   ```bash
   cp Database/drinkoo.db Database/drinkoo.db.backup.$(date +%s)
   ```

2. **Restore from Backup**

   ```bash
   cp Database/drinkoo.db.backup.<timestamp> Database/drinkoo.db
   ```

3. **Verify Data Integrity**
   ```bash
   python -m pytest Tests/test_database.py -v
   ```

### Git Revert for Clean History

1. **Create Revert Commit**

   ```bash
   git revert <bad_commit_hash>
   ```

2. **Test Revert**

   ```bash
   pytest Tests/ -v
   ```

3. **Deploy Revert**
   ```bash
   git push origin main
   ```

---

## 8. Documentation Evidence

### Startup Output Example

```
============================================================
Starting DRINKOO RAG Chatbot API v1.0.0
Environment: development
============================================================
Configuration validated successfully
Connected to database: Database/drinkoo.db
Database tables: 8
RAG service ready
Listening on http://0.0.0.0:8000
```

### Health Check Output Example

```bash
$ curl http://localhost:8000/health | jq
{
  "status": "healthy",
  "timestamp": "2026-06-14T10:00:00.000Z",
  "api_version": "1.0.0",
  "environment": "development",
  "database": {
    "status": "healthy",
    "message": "Database ready (8 tables)",
    "tables_count": 8,
    "can_read": true,
    "can_write": true
  },
  "rag_ready": true
}
```

### Log Example

```
2026-06-14 10:00:00,123 - backend.app.main - INFO - Starting DRINKOO RAG Chatbot API v1.0.0
2026-06-14 10:00:00,456 - backend.config - INFO - Configuration validated successfully
2026-06-14 10:00:00,789 - backend.database - INFO - Connected to database: Database/drinkoo.db
2026-06-14 10:00:05,012 - backend.auth - INFO - User signed up: alice (ID: 1)
2026-06-14 10:00:10,345 - backend.auth - INFO - User logged in: alice (ID: 1)
2026-06-14 10:00:15,678 - backend.rag_service - INFO - Retrieved 3 support articles for query: orange juice
2026-06-14 10:00:20,901 - backend.app.routers.chatbot - INFO - Chatbot query processed for alice: 3 context items
```

---

## 9. Recommendations

### Short Term (Development)

- ✅ Implement `/health` endpoint (DONE)
- ✅ Implement `/status` endpoint (DONE)
- ✅ Setup structured logging (DONE)
- [ ] Add request/response logging middleware
- [ ] Setup local log rotation
- [ ] Create monitoring dashboard template

### Medium Term (Pre-Production)

- [ ] Integrate APM tool (Datadog/New Relic)
- [ ] Setup centralized logging (ELK Stack)
- [ ] Configure alerting rules
- [ ] Create runbooks for common issues
- [ ] Implement rate limiting
- [ ] Add request tracing

### Long Term (Production)

- [ ] Implement distributed tracing (Jaeger)
- [ ] Setup synthetic monitoring
- [ ] Implement SLO tracking
- [ ] Automate scaling based on metrics
- [ ] Implement anomaly detection
- [ ] Conduct load testing

---

## 10. Contact & Escalation

| Role             | Responsibility              | Contact |
| ---------------- | --------------------------- | ------- |
| Backend Engineer | Code & API health           | TBD     |
| DevOps Engineer  | Infrastructure & deployment | TBD     |
| Database Admin   | Database performance        | TBD     |
| On-Call          | Emergency response          | TBD     |

---

## 11. Change Log

| Date       | Change                     | Author         |
| ---------- | -------------------------- | -------------- |
| 2026-06-14 | Initial observability plan | GitHub Copilot |

---

## Appendix: Health Check Test Commands

### Test API Health

```bash
curl http://localhost:8000/health
```

### Test Status Endpoint

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/status
```

### Test Version

```bash
curl http://localhost:8000/version
```

### Monitor Logs

```bash
tail -f logs/drinkoo.log
tail -f logs/drinkoo.log | grep ERROR
tail -f logs/drinkoo.log | grep -i chatbot
```

### Check Database Health

```bash
python -c "from backend.database import check_db_health; import json; print(json.dumps(check_db_health(), indent=2))"
```

---

_End of Observability Plan_
