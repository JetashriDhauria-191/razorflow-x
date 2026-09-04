# 🧪 RAZORFLOW X — Quality Assurance, Testing Protocol & Audit Report

This document describes the automated test suites, verification scripts, and quality assurance protocols implemented in **RAZORFLOW X**.

---

## 📊 Automated Test Suite Summary

| Test Suite | Scope & Module | Test Count | Status | Execution Time |
| :--- | :--- | :--- | :--- | :--- |
| **Pytest Automated Suite** | Unit & Endpoint Tests | **42 / 42** | **100% PASSED** | ~10.5 seconds |
| **Master QA Audit Suite** | Full System & Event Handlers | **10 / 10 Modules** | **100% PASSED** | ~6.8 seconds |
| **Frontend Event Handlers** | HTML DOM Event Bindings | **249 Handlers** | **100% VERIFIED** | Instant |
| **Cryptographic Audit Chain** | SHA-256 Merkle Chain | **1,228+ Events** | **100% VALID** | Instant |
| **Growth A/B Simulation** | Monte Carlo (1k Sessions) | **1,000 Sessions** | **100% CONVERGED** | ~0.5 seconds |

---

## 🏃 1. Running the Automated Pytest Suite

```bash
# Execute all 42 automated tests
pytest -v
```

### Verified Test Breakdown:
1. `tests/test_agentic_checkout.py`: Intent parsing, cross-sell discovery, bounded checkout order creation (`PASSED`).
2. `tests/test_auth.py`: Password hashing, user registration, JWT token login (`PASSED`).
3. `tests/test_campaigns.py`: Promotional campaign proposal generation (`PASSED`).
4. `tests/test_catalogue.py`: Category search, budget constraints, SKU details, and image integrity (`PASSED`).
5. `tests/test_experiments.py`: 1,000-session Monte Carlo A/B simulation (`PASSED`).
6. `tests/test_failure.py`: 504 gateway timeout failure analysis, bank downtime detection (`PASSED`).
7. `tests/test_growth_engine.py`: Dynamic bundle generation, AOV optimization (`PASSED`).
8. `tests/test_ml.py`: Real-time reliability inference, metric structures (`PASSED`).
9. `tests/test_multilingual_intelligence.py`: 8-tier phonetic ladder, Levenshtein distance, transliteration (`PASSED`).
10. `tests/test_payments.py`: Razorpay order creation, HMAC signature verification, simulated failure (`PASSED`).
11. `tests/test_policy_gate.py`: Spending caps, discount bounds, unconfirmed action blocks (`PASSED`).
12. `tests/test_recommender.py`: Explainable scoring, budget constraint filtering (`PASSED`).
13. `tests/test_recovery.py`: Autonomous recovery execution, circuit breaker tripping (`PASSED`).
14. `tests/test_reliability_os.py`: Reliability score, preventive intelligence, digital twin, explainability (`PASSED`).
15. `tests/test_risk.py`: Low risk and high risk transaction evaluation (`PASSED`).
16. `tests/test_webhooks.py`: Inbound webhook processing, signature tampering detection (`PASSED`).

---

## 🎯 2. Running the Master Comprehensive QA Audit Suite

```bash
python tests/master_audit_suite.py
```

### Verified Audit Modules:
- **Module 1: HTML Event Handlers Audit**: Scans `index.html` and asserts all 249 event handlers map to genuine JavaScript functions (`98 unique functions verified`).
- **Module 2: Product Catalogue & Recommendation Diversity**: Asserts zero duplicate imagery and valid category mappings across 183 products.
- **Module 3: Agent-to-Agent Commerce Multi-Turn Audit**: Executes a 6-turn negotiation between Buyer Agent and Merchant Agent and confirms pre-flight hold.
- **Module 4: Payment Reliability Lab (7 Chaos Scenarios)**:
  - 504 Gateway Timeout ➔ `RECOVERY_PENDING` (Auto-Retry backoff verified)
  - Network Socket Drop ➔ `RECOVERY_PENDING` (Idempotent reconnect verified)
  - Duplicate Click Race ➔ `SUCCESS` (Atomic dedup, 0 double billing verified)
  - Card Declined ➔ `RECOVERY_PENDING` (1-Click UPI fallback verified)
  - Webhook Processing Delay ➔ `SUCCESS` (Proactive order reconciliation verified)
  - Webhook Signature Tampering ➔ `FAILED` (Security shield block verified)
  - Bounded Retry Limit ➔ `FAILED` (Circuit breaker halt verified)
- **Module 5: Money Safety Gate Audit**: Verifies hard spending caps (₹20,000) and discount caps (25%).
- **Module 6: Verifiable Audit Trail Cryptographic Chain**: Validates SHA-256 Merkle chain integrity across 1,228+ events.
- **Module 7: Growth Experiment 1,000-Session Live Simulation**: Confirms baseline conversion 3.31% vs Razorflow X 9.01% (+172.2% lift, $p < 0.001$).
- **Module 8: Growth Command Center & Revenue Simulator**: Verifies growth copilot and live ROI calculator.
- **Module 9: Closed-Loop Commerce Intelligence Matrix**: Confirms 4-stage adaptive weight tuning.
- **Module 10: Transaction Ledger Balance Invariant**: Confirms zero drift across double-entry debits and credits.

---

## 💳 3. Razorpay Test Mode Verification

To verify real interaction with Razorpay's sandbox:
1. Ensure `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are set in `.env`.
2. Start the backend: `python -m uvicorn backend.main:app --port 8080`.
3. Open `http://127.0.0.1:8080/`.
4. Click **Instant 1-Click Buy** on any product.
5. In the Razorpay modal, select **Card** (use standard test card: `4111 1111 1111 1111`, any future expiry, OTP `123456`) or **UPI QR**.
6. Observe the green verified white receipt modal upon server signature confirmation.
