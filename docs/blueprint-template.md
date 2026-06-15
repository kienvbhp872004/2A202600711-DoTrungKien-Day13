# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: 2A202600711-DoTrungKien
- [REPO_URL]: https://github.com/kienvbhp872004/2A202600711-DoTrungKien-Day13
- [MEMBERS]:
  - Đỗ Trung Kiên | Role: Logging & PII, Tracing & Enrichment, SLO & Alerts, Load Test & Dashboard, Demo & Report

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/images/screenshot_correlation_id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/images/screenshot_pii_redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/images/screenshot_trace_waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: The `run` span in agent.py covers the full pipeline: RAG retrieval → LLM generation. During the `rag_slow` incident, the RAG sub-span took ~5000ms vs the normal ~50ms, making it the clear bottleneck. This was visible in Langfuse as a wide span at the top of the waterfall.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/images/screenshot_dashboard.png
- [DASHBOARD_LATENCY]: docs/images/Latency.png
- [DASHBOARD_TRAFFIC]: docs/images/Traffic.png
- [DASHBOARD_COST]: docs/images/Cost over time.png
- [DASHBOARD_TOKENS]: docs/images/Tokens InOut.png
- [DASHBOARD_QUALITY]: docs/images/Quality Score.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | ~160ms (normal) / ~5300ms (incident) |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | ~$0.04 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/images/screenshot_alert_rules.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 tăng đột ngột từ ~160ms lên ~5300ms sau khi inject incident. Traffic vẫn bình thường, không có error — chứng tỏ hệ thống còn sống nhưng chậm bất thường.
- [ROOT_CAUSE_PROVED_BY]: Traces trên Langfuse cho thấy span `run` kéo dài ~5300ms. Sub-span RAG retrieval chiếm toàn bộ thời gian đó. Incident toggle `rag_slow=True` được xác nhận qua endpoint `GET /health`.
- [FIX_ACTION]: Tắt incident toggle bằng lệnh `python scripts/inject_incident.py --scenario rag_slow --disable`. Latency trở về ~160ms ngay lập tức.
- [PREVENTIVE_MEASURE]: Đặt timeout cứng cho RAG retrieval (ví dụ 2000ms), fallback sang kết quả cache khi vượt ngưỡng. Alert `high_latency_p95` sẽ bắn sau 30 phút nếu P95 > 5000ms.

---

## 5. Individual Contributions & Evidence

### Đỗ Trung Kiên
- [TASKS_COMPLETED]:
  - Implement Correlation ID middleware (`app/middleware.py`): sinh `req-<8hex>`, bind structlog context, trả về headers `x-request-id` và `x-response-time-ms`
  - Enrich logs với request context (`app/main.py`): bind `user_id_hash`, `session_id`, `feature`, `model`, `env`
  - Kích hoạt PII scrubbing processor (`app/logging_config.py`): lọc email, SĐT, CCCD, thẻ tín dụng khỏi toàn bộ log
  - Fix Langfuse v3 API (`app/tracing.py`): migrate từ `langfuse.decorators` sang `from langfuse import observe`
  - Cấu hình SLO và 4 alert rules (`config/slo.yaml`, `config/alert_rules.yaml`)
  - Viết runbook cho 4 alerts (`docs/alerts.md`)
  - Xây 6-widget dashboard trên Langfuse
  - Validate score: 100/100 (`python scripts/validate_logs.py`)
- [EVIDENCE_LINK]: 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Dùng `hash_user_id()` để rút ngắn user identifier trong traces, giảm payload size. Cost trung bình ~$0.0022/request.
- [BONUS_AUDIT_LOGS]: Cấu hình `AUDIT_LOG_PATH=data/audit.jsonl` trong `.env` để tách audit log riêng khỏi application log.
- [BONUS_CUSTOM_METRIC]: Thêm `quality_score` vào mỗi trace via `langfuse_context.update_current_observation()`, hiển thị trong dashboard widget "Quality Score avg".
