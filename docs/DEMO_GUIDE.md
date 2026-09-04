# 🎬 RAZORFLOW X — Hackathon Demo Guide

This guide gives you a clean, step-by-step walkthrough to demonstrate all key features of **RAZORFLOW X** in 3 minutes.

---

## ⏱️ 3-Minute Demo Script

### Step 1: Open the Application (0:00 - 0:30)
1. Open your browser and go to **[http://127.0.0.1:8080/](http://127.0.0.1:8080/)**.
2. Point out the top header:
   - Live Wallet balance (₹1,00,000.00 test wallet).
   - Razorpay Test SDK status indicator.
   - Quick navigation tabs across all 10 modules.

### Step 2: Conversational Checkout & Growth Brain (0:30 - 1:00)
1. In the search box, try typing or saying:
   - *"Find running shoes under 5000"* or *"சட்டை வேண்டும்"* (Tamil) or *"Jhootha"* (Hindi).
2. Point out the **Growth Brain 6-Point Tree**:
   - `Primary Pick`: The most relevant product.
   - `Budget Saver`: Affordable alternative.
   - `Best Value`: Highest composite score.
   - `Pro Flagship`: Premium option.
   - `Smart Upsell` & `Bundle Cross-Sell`: Relevant accessories with combo discounts.
3. Click **`+ Add to Cart`** $	o$ select quantity $(1, 2, 3)$ $	o$ observe that the cart increments accurately without duplicate rows.

### Step 3: Agent-to-Agent Commerce (1:00 - 1:40)
1. Switch to **Tab 3: Agent-to-Agent Commerce**.
2. Click **`▶️ Run Autonomous Live A2A Dialogue`**.
3. Watch the 6-turn negotiation between 👤 **Buyer Agent** and 🏪 **Merchant Agent**:
   - Turn 1: Buyer formulates intent and budget limit.
   - Turn 2: Merchant locks catalog stock.
   - Turn 3: Buyer evaluates warranty and SLA.
   - Turn 4: Merchant attaches an approved combo discount.
   - Turn 5: Buyer accepts the proposal.
   - Turn 6: **Safety Gate Hold** pauses execution until the user clicks explicit confirmation.

### Step 4: Payment Reliability Lab (1:40 - 2:20)
1. Switch to **Tab 4: Payment Reliability Lab**.
2. Click **`1. Gateway Timeout (504)`**:
   - Notice the state transition in the log: `PENDING` $	o$ `504 TIMEOUT DETECTED` $	o$ `AUTONOMOUS RECOVERY VIA SECONDARY UPI` $	o$ `FUNDS RESTORED`.
3. Try **`3. Duplicate Click Race`**:
   - Demonstrates 256-bit idempotency locking that blocks double-charging during rapid clicks.
4. Try **`6. Signature Tamper`**:
   - Demonstrates HMAC-SHA256 rejection when a webhook payload signature is altered.

### Step 5: Verifiable Audit Trail & Growth Lab (2:20 - 3:00)
1. Switch to **Tab 7: Verifiable Audit Trail**.
   - Click **`🔐 Verify Cryptographic Chain`** to audit all blocks. Shows that every event hash matches and the SHA-256 chain is valid.
2. Switch to **Tab 5: Growth Command Center**.
   - Scroll to **🧪 Growth Experiment Lab**.
   - Click **`⚡ Run 1,000-Session Live Simulation`** to see dynamic benchmark results comparing traditional storefronts against Razorflow X (+156% conversion uplift, ₹48k+ salvaged GMV).
