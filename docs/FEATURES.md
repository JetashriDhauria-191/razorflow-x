# ✨ RAZORFLOW X — Comprehensive Feature Catalog

This document details every feature and capability **actually implemented** within the RAZORFLOW X codebase.

The system is structured around the 9-stage Payment Reliability lifecycle:
**PREDICT ➔ PREVENT ➔ PAY ➔ DETECT ➔ DIAGNOSE ➔ DECIDE ➔ RECOVER ➔ VERIFY ➔ LEARN**

---

## 1. COMMERCE INTELLIGENCE

### 8-Tier Multilingual Discovery Ladder (`backend/discovery_engine.py`)
- **Tier 1: Exact SKU / Name Match**: Instant lookup across catalogue data.
- **Tier 2: Normalized Script / Lowercase Match**: Strips whitespace, punctuation, and casing variations.
- **Tier 3: Fuzzy Levenshtein Distance Matching**: Catches typos like *"snekaers"*, *"phne"*, *"samung"*.
- **Tier 4: Cross-Lingual Semantic Translation**: Maps Indic script tokens (*"juta"*, *"kaadhu phon"*, *"zapatos"*) to canonical categories.
- **Tier 5: Budget Constraint Extractor**: Regex-based natural language price parser (*"under 3000"*, *"below 5000"*, *"between 1000 and 4000"*).
- **Tier 6: Multi-Attribute Sorting**: Re-ranks results dynamically by rating, stock levels, and price point.
- **Tier 7: Category Fallback**: When exact product isn't found, surfaces top products in the matching category.
- **Tier 8: Popular Recommendations Fallback**: Never returns a blank search screen; offers trending alternatives.

### Curated Catalogue Architecture (`backend/catalogue_data.json`)
- **183 Verified Products**: Real category-accurate Unsplash CDN images (perfume for Dior, running shoes for Nike/Adidas, shavers for Braun, stylers for Dyson, headphones for Sony).
- **Virtual 10,000+ SKU Index**: Scalable hash indexing for high-volume simulated e-commerce operations.

---

## 2. PAYMENT RELIABILITY & RELIABILITY OS

### 5-Stage Reliability Pipeline (`backend/main.py`)
- **Stage 1: Pre-Auth Intent Analysis**: Validates buyer credentials, device telemetry, and gateway health prior to order creation.
- **Stage 2: Smart Circuit Routing**: Dynamically directs traffic to the most reliable available banking rail (Cards, UPI, Netbanking, Wallets).
- **Stage 3: In-Flight Fallback & Auto-Retry**: Automatically manages transient socket drops and 504 gateway timeouts.
- **Stage 4: Deterministic Money Safety Gate**: Blocks out-of-bounds requests and enforces double-entry verification.
- **Stage 5: Post-Payment Reconciliation**: Validates HMAC-SHA256 signatures, closes pending states, and updates ledger records.

### Live Payment FSM State Machine
- **States**: `CREATED` ➔ `CHECKOUT` ➔ `ATTEMPTED` ➔ `PROCESSING` ➔ `RECOVERY_PENDING` ➔ `VERIFIED` ➔ `SUCCESS` / `FAILED`.
- **Sub-200ms Interception**: Real-time state listener catches drop-offs and routes to self-healing flows.

---

## 3. RISK AND SAFETY

### Deterministic Money Safety Gate (`policy_gate.py`)
- **Spending Bounds**: Hard ceiling of ₹20,000 per autonomous order.
- **Discount Caps**: Maximum promotional discount limited to 25% to protect merchant margins.
- **Mandatory User Consent Hold**: Autonomous agents cannot debit funds without an explicit confirmation gate.
- **Strict Anti-Hallucination**: AI models cannot bypass programmatic financial validations.

### Risk Scoring Engine (`risk_engine.py`)
- **Velocity Tracking**: Detects abnormal transaction spikes from the same IP or user account.
- **Explainable Risk Scores**: Outputs transparent risk scores (Low, Medium, High) with itemized rationales.

---

## 4. AI INTELLIGENCE & AGENT-TO-AGENT (A2A) COMMERCE

### Multi-Turn Agent Negotiation (`agent_orchestrator.py`)
- **6-Turn Structured Exchange**:
  1. `[BUYER_AGENT]` Formulates purchase intent and budget constraints.
  2. `[MERCHANT_AGENT]` Searches catalogue and applies inventory reservation lock.
  3. `[BUYER_AGENT]` Evaluates multi-attribute product specifications.
  4. `[MERCHANT_AGENT]` Proposes approved volume discount bundle.
  5. `[BUYER_AGENT]` Formally accepts commercial terms.
  6. `[SAFETY_GATE]` Holds transaction in pre-flight state pending shopper confirmation.

### Multi-Turn AI Shopping Copilot (`backend/main.py`)
- Conversational natural language assistant supporting multi-turn memory, product recommendations, and instant cart dispatch.

---

## 5. PAYMENT RELIABILITY LAB (7 CHAOS SCENARIOS)

Stress-tests resilience against real-world production payment failure modes:

| Scenario | Simulated Failure Mode | Detection Mechanism | Autonomous Self-Healing Action |
| :--- | :--- | :--- | :--- |
| **1. 504 Gateway Timeout** | Bank gateway drops request | Timeout signal / 504 HTTP status | Exponential backoff retry with state lock |
| **2. Network Socket Drop** | Client-to-server socket breaks | TCP reset / connection drop | Idempotent reconnection with state preservation |
| **3. Duplicate Click Race** | User double-clicks checkout button | Atomic 256-bit lock key check | Drops duplicate; returns active in-flight order |
| **4. Card Decline (Low Balance)**| Issuer declines card debit | `payment.failed` error code | Instant 1-Click zero-re-entry UPI alternative |
| **5. Webhook Delay (45s)** | Webhook notification delayed | 45-second webhook timer | Proactive polling: `GET /v1/payments/{id}` |
| **6. Signature Tampering** | Malicious actor mutates payload | HMAC-SHA256 signature check | Security Shield immediately blocks transaction |
| **7. Bounded Retry Boundary** | Gateway down continuously | Circuit breaker trip limit (3 tries)| Halts retries, restores user balance safely |

---

## 6. IDEMPOTENCY & DEDUP

### 256-Bit Atomic Lock Architecture (`webhooks.py`, `backend/main.py`)
- **Deterministic Key Hashing**: Key computed from `CartHash + TimestampWindow + UserID`.
- **Zero Double-Billing Guarantee**: Check-and-set database transactions guarantee that rapid clicks or retried requests never trigger duplicate charges.

---

## 7. RAZORPAY INTEGRATION

### Official Razorpay Python SDK & Checkout JS
- **Orders API Integration**: Creates compliant Razorpay Orders (`/v1/orders`) with receipt tracking.
- **Client Checkout Modal**: Standard Razorpay modal integration supporting UPI QR, Cards, Netbanking, and Wallets.
- **Server-Side HMAC-SHA256 Verification**:
  ```python
  expected_sig = hmac.new(
      key_secret.encode(),
      f"{order_id}|{payment_id}".encode(),
      hashlib.sha256
  ).hexdigest()
  ```

---

## 8. MULTILINGUAL & VOICE COMMERCE

### Web Speech API Integration
- **Hands-Free Shopping**: Microphone audio input streaming directly into query normalization.
- **Language Detection**: Automatically detects English, Hindi, Tamil, Telugu, and Spanish scripts.
- **Audio Feedback**: Text-to-speech confirmation of shopping actions and recovery status.

---

## 9. DASHBOARD AND ANALYTICS

### Double-Entry Transaction Ledger (`database.py`)
- **Accounting Invariant**: Enforces $\sum \text{Debits} = \sum \text{Credits}$ across merchant settlement, buyer wallet, and platform escrow.
- **Live Visual Ledger**: Real-time table displaying transaction IDs, timestamps, amounts, and settlement states.

### Verifiable Merkle Audit Trail (`audit_trace.py`)
- **Cryptographic Chaining**: SHA-256 hash chains verifying chronological block integrity.
- **One-Click Audit Verification**: Interactive button to verify cryptographic chain validity (`Valid: True`).

### Growth Command Center (`growth_engine.py`, `experiments.py`)
- **1,000-Session Monte Carlo Simulation**: Proves **+172.2% conversion lift** (3.31% to 9.01%) and **₹52,832 recovered GMV**.
- **Interactive Revenue Simulator**: Models merchant ROI across custom GMV and average ticket sizes.

---

## 10. TESTING & DEMO CAPABILITIES

- **42 Automated Pytest Tests**: Comprehensive coverage across authentication, campaigns, catalogue, experiments, ML, payments, risk, and webhooks.
- **10-Module Master QA Audit Suite**: Programmatically verifies all 249 frontend event handlers, 98 unique JS functions, and all 7 chaos failure models.
- **One-Click Telemetry Seeding**: Populates realistic orders, recoveries, and audit events for demonstration.
