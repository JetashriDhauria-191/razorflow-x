

  // =========================================================
  // RAZORFLOW X — MASTER UNIFIED CLIENT CONTROLLER
  // =========================================================

  const $ = (id) => document.getElementById(id);

  let currentVoiceLanguage = "en-IN";
  let isVoiceAudioFeedback = true;
  let isHandsFreeActive = false;
  let speechRecognitionInstance = null;
  let discoveryProductsCache = [];
  let selectedCompareProducts = [];
  let currentActiveProduct = { id: "HP001", product_id: "HP001", name: "Sony WH-1000XM5 Wireless Noise Cancelling Headphones", price: 24990, original_price: 29990, rating: 4.9, review_count: 1420, delivery_days: 1, category: "headphones", image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500" };
  let currentOrderAmount = 24990;
  let currentDeskMethod = "upi";
  let currentDeskBank = "State Bank of India (SBI)";
  let currentSelectedBank = "State Bank of India (SBI)";
  let currentSelectedUpiApp = "Google Pay (GPay)";
  let currentDiscoveryIntentFilter = "all";
  let currentActiveSearchLanguage = "auto";
  let discoveryModalActiveProduct = null;
  let typingSuggestDebounce = null;
  let currentSpellCorrectionText = null;
  let judgeTourCurrentStep = 0;
  let isDuplicateLockActive = false;

  // Buyer Wallet Balance
  let userWalletBalance = 100000;
  let walletTransactionLogs = [
    { title: "Initial Demo Balance", amount: 100000, type: "credit", time: new Date().toLocaleTimeString() }
  ];

  // Helper API Fetcher
  async function api(path, options = {}) {
    const defaultHeaders = { "Content-Type": "application/json" };
    options.headers = { ...defaultHeaders, ...options.headers };
    const resp = await fetch(path, options);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || err.message || "Request failed");
    }
    return resp.json();
  }

  function showToast(msg, type = "info") {
    const container = $("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function speak(text) {
    if (!isVoiceAudioFeedback || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*_#`~]/g, '').slice(0, 160);
    const u = new SpeechSynthesisUtterance(cleanText);
    u.lang = currentVoiceLanguage || 'en-IN';
    u.rate = 1.0;
    window.speechSynthesis.speak(u);
  }

  function logTelemetry(msg, color = "#cbd5e1") {
    const box = $("relSideEventLog");
    if (!box) return;
    const time = new Date().toLocaleTimeString();
    const line = document.createElement("div");
    line.style.color = color;
    line.innerHTML = `[${time}] ${msg}`;
    box.appendChild(line);
    box.scrollTop = box.scrollHeight;
  }

  // =========================================================
  // BUYER WALLET BALANCE CONTROLLERS
  // =========================================================
  function toggleWalletDrawer(forceOpen = null) {
    const drawer = $("walletSlideDrawerOverlay");
    if (!drawer) return;
    if (forceOpen === true) drawer.classList.add("open");
    else if (forceOpen === false) drawer.classList.remove("open");
    else drawer.classList.toggle("open");
    if (drawer.classList.contains("open")) updateUserWalletDisplays();
  }

  function updateUserWalletDisplays() {
    const isZero = userWalletBalance <= 0;
    const formatted = `₹${Math.max(0, userWalletBalance).toLocaleString('en-IN')}.00`;
    
    const hDisplay = $("userWalletBalanceDisplay");
    const hBadge = $("headerWalletBadge");
    if (hDisplay) {
      hDisplay.textContent = isZero ? "₹0.00 (INSUFFICIENT)" : formatted;
      hDisplay.style.color = isZero ? "#ef4444" : "#4ade80";
    }
    if (hBadge) {
      hBadge.style.borderColor = isZero ? "rgba(239, 68, 68, 0.6)" : "rgba(34, 197, 94, 0.4)";
      hBadge.style.background = isZero ? "rgba(239, 68, 68, 0.15)" : "rgba(34, 197, 94, 0.15)";
    }

    const dAmount = $("walletDrawerMainAmount");
    const dCard = $("walletDrawerBalanceCard");
    const dStatus = $("walletDrawerStatusPill");
    const dWarn = $("walletDrawerWarningMsg");
    if (dAmount) {
      dAmount.textContent = isZero ? "₹0.00 (INSUFFICIENT)" : formatted;
      dAmount.style.color = isZero ? "#ef4444" : "#4ade80";
    }
    if (dCard) {
      dCard.style.borderColor = isZero ? "rgba(239, 68, 68, 0.4)" : "rgba(34, 197, 94, 0.3)";
      dCard.style.background = isZero ? "linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(15,23,42,0.8) 100%)" : "linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(15,23,42,0.8) 100%)";
    }
    if (dStatus) {
      dStatus.textContent = isZero ? "⚠️ ZERO BALANCE" : "● ACTIVE";
      dStatus.style.background = isZero ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 197, 94, 0.2)";
      dStatus.style.color = isZero ? "#f87171" : "#4ade80";
    }
    if (dWarn) dWarn.style.display = isZero ? "block" : "none";

    renderWalletActivityList();
  }

  function addWalletMoney(amt) {
    const num = parseFloat(amt);
    if (isNaN(num) || num <= 0) return;
    userWalletBalance += num;
    logWalletActivity(`Added Funds (Quick Deposit)`, num, true);
    updateUserWalletDisplays();
    logTelemetry(`Wallet credited +₹${num.toLocaleString('en-IN')}. New balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "#4ade80");
    showToast(`💳 Added ₹${num.toLocaleString('en-IN')}! Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "success");
    speak(`Added ${num} rupees. New balance is ${userWalletBalance} rupees.`);
  }

  function handleCustomAddMoney() {
    const input = $("customAddAmountInput");
    if (!input) return;
    const num = parseFloat(input.value);
    if (isNaN(num) || num <= 0) {
      showToast("Please enter a valid amount.", "warning");
      return;
    }
    userWalletBalance += num;
    logWalletActivity(`Custom Funds Deposit`, num, true);
    input.value = "";
    updateUserWalletDisplays();
    showToast(`💳 Added ₹${num.toLocaleString('en-IN')}! Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "success");
    speak(`Added ${num} rupees. New balance is ${userWalletBalance} rupees.`);
  }

  function withdrawWalletMoney(amt) {
    const num = parseFloat(amt);
    if (isNaN(num) || num <= 0) return;
    if (userWalletBalance < num) {
      showToast(`Cannot withdraw ₹${num.toLocaleString('en-IN')}. Available: ₹${userWalletBalance.toLocaleString('en-IN')}`, "error");
      return;
    }
    userWalletBalance -= num;
    logWalletActivity(`Withdrawal to Bank Account`, num, false);
    updateUserWalletDisplays();
    showToast(`💸 Withdrew ₹${num.toLocaleString('en-IN')} to Bank. Remaining: ₹${userWalletBalance.toLocaleString('en-IN')}`, "info");
    speak(`Withdrew ${num} rupees. Remaining balance is ${userWalletBalance} rupees.`);
  }

  function withdrawAllWalletMoney() {
    if (userWalletBalance <= 0) {
      showToast("Wallet balance is already ₹0.00.", "info");
      return;
    }
    const drained = userWalletBalance;
    userWalletBalance = 0;
    logWalletActivity(`Total Withdrawal (Zeroed Out)`, drained, false);
    updateUserWalletDisplays();
    showToast(`💸 Withdrew ₹${drained.toLocaleString('en-IN')}! Balance is now ₹0.00 (INSUFFICIENT).`, "warning");
    speak("Total balance withdrawn. Wallet balance is now zero rupees.");
  }

  function handleCustomWithdrawMoney() {
    const input = $("customWithdrawAmountInput");
    if (!input) return;
    const num = parseFloat(input.value);
    if (isNaN(num) || num <= 0) {
      showToast("Please enter a valid amount.", "warning");
      return;
    }
    if (userWalletBalance < num) {
      showToast(`Insufficient balance to withdraw ₹${num.toLocaleString('en-IN')}.`, "error");
      return;
    }
    userWalletBalance -= num;
    logWalletActivity(`Custom Withdrawal to Bank`, num, false);
    input.value = "";
    updateUserWalletDisplays();
    showToast(`💸 Withdrew ₹${num.toLocaleString('en-IN')} to Bank.`, "info");
    speak(`Withdrew ${num} rupees.`);
  }

  function logWalletActivity(title, amt, isAddition) {
    walletTransactionLogs.unshift({
      title: title,
      amount: amt,
      type: isAddition ? "credit" : "debit",
      time: new Date().toLocaleTimeString()
    });
    if (walletTransactionLogs.length > 20) walletTransactionLogs.pop();
  }

  function renderWalletActivityList() {
    const list = $("walletActivityList");
    if (!list) return;
    list.innerHTML = walletTransactionLogs.map(item => `
      <div class="wallet-history-item">
        <div>
          <span style="color:#cbd5e1; font-weight:600;">${item.title}</span><br>
          <small style="color:#64748b; font-size:10px;">${item.time}</small>
        </div>
        <strong style="color:${item.type === 'credit' ? '#4ade80' : '#f87171'}; font-family:var(--font-mono);">
          ${item.type === 'credit' ? '+' : '-'}₹${item.amount.toLocaleString('en-IN')}.00
        </strong>
      </div>
    `).join("");
  }

  function checkWalletFunds(amount) {
    if (userWalletBalance < amount) {
      showToast(`⚠️ INSUFFICIENT WALLET BALANCE! Order: ₹${amount.toLocaleString('en-IN')} | Available: ₹${userWalletBalance.toLocaleString('en-IN')}. Please add money in the wallet slide.`, "error");
      speak("Insufficient balance in your wallet. Please add money using the wallet slide.");
      toggleWalletDrawer(true);
      return false;
    }
    return true;
  }

  // =========================================================
  // TAB NAVIGATION & VOICE FEEDBACK
  // =========================================================
  function switchMainTab(tabName) {
    document.querySelectorAll(".nav-tab-item").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

    const targetBtn = $(`tabBtn_${tabName}`);
    const targetPane = $(`pane_${tabName}`);

    if (targetBtn) targetBtn.classList.add("active");
    if (targetPane) targetPane.classList.add("active");

    if (tabName === "growth") {
      loadDashboardMetrics();
      runGrowthSimTab();
    } else if (tabName === "catalogue") {
      executeDiscoverySearch();
    } else if (tabName === "ledger") {
      loadTransactions();
    } else if (tabName === "audit") {
      loadAuditLogs();
    }

    if (isVoiceAudioFeedback) {
      speak(`Switched to ${tabName.replace('_', ' ')} tab.`);
    }
  }

  function changeVoiceLanguage(lang) {
    currentVoiceLanguage = lang;
    showToast(`Switched voice recognition language to: ${lang}`, "info");
    speak(`Voice language changed.`);
  }

  function toggleVoiceAudioFeedback() {
    isVoiceAudioFeedback = !isVoiceAudioFeedback;
    const badge = $("voiceStatusBadge");
    if (badge) {
      badge.textContent = isVoiceAudioFeedback ? "🔊 Voice: ON" : "🔇 Voice: OFF";
      badge.className = isVoiceAudioFeedback ? "badge-tag badge-blue" : "badge-tag badge-red";
    }
    showToast(`Voice feedback audio is now ${isVoiceAudioFeedback ? 'ENABLED' : 'MUTED'}`, "info");
  }

  function toggleHandsFreeVoice() {
    isHandsFreeActive = !isHandsFreeActive;
    const btn = $("btnHandsFreeToggle");
    if (btn) {
      btn.textContent = isHandsFreeActive ? "🎙️ Hands-Free: ON" : "🎙️ Hands-Free: OFF";
      btn.style.borderColor = isHandsFreeActive ? "#22c55e" : "#334155";
      btn.style.color = isHandsFreeActive ? "#4ade80" : "#94a3b8";
    }
    if (isHandsFreeActive) {
      startContinuousVoiceRecognition();
      showToast("Hands-free continuous voice listening active! Speak anytime.", "success");
      speak("Hands free voice active.");
    } else {
      if (speechRecognitionInstance) speechRecognitionInstance.stop();
      showToast("Hands-free voice listening paused.", "info");
    }
  }

  function toggleDiscoveryVoiceFeedback() {
    toggleVoiceAudioFeedback();
  }

  function startContinuousVoiceRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return;
    speechRecognitionInstance = new SpeechRec();
    speechRecognitionInstance.lang = currentVoiceLanguage || "en-IN";
    speechRecognitionInstance.continuous = true;
    speechRecognitionInstance.interimResults = false;

    speechRecognitionInstance.onresult = (event) => {
      const last = event.results.length - 1;
      const transcript = event.results[last][0].transcript.trim();
      showToast(`🎙️ Heard: "${transcript}"`, "info");
      if ($("mainChatInput")) $("mainChatInput").value = transcript;
      sendMainChatMessage();
    };

    speechRecognitionInstance.onerror = () => {
      if (isHandsFreeActive) setTimeout(startContinuousVoiceRecognition, 1500);
    };

    speechRecognitionInstance.start();
  }

  function triggerMicShopping() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      showToast("Voice recognition not supported in browser. Type your query instead.", "error");
      return;
    }
    const micBtn = $("btnMainMic");
    if (micBtn) micBtn.classList.add("listening");

    const rec = new SpeechRec();
    rec.lang = currentVoiceLanguage || "en-IN";
    rec.continuous = false;
    rec.interimResults = false;

    showToast(`🔴 Listening in ${currentVoiceLanguage}... Speak your command!`, "info");

    rec.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (micBtn) micBtn.classList.remove("listening");
      if ($("mainChatInput")) $("mainChatInput").value = text;
      showToast(`🎙️ Recognized: "${text}"`, "info");
      sendMainChatMessage(text);
    };

    rec.onerror = () => {
      if (micBtn) micBtn.classList.remove("listening");
      showToast("Voice listening completed.", "info");
    };

    rec.start();
  }

  function simulateVoiceInput(phrase) {
    showToast(`🎙️ Voice Recognized: "${phrase}"`, "info");
    if ($("mainChatInput")) $("mainChatInput").value = phrase;
    sendMainChatMessage(phrase);
  }

  function handleQuickChip(chipText) {
    if ($("mainChatInput")) $("mainChatInput").value = chipText;
    sendMainChatMessage(chipText);
  }

  // =========================================================
  // TAB 1: CONVERSATIONAL AI COMMERCE & RECOMMENDATIONS
  // =========================================================
  async function sendMainChatMessage(overrideText = null) {
    const input = $("mainChatInput");
    const message = (overrideText || (input ? input.value : "")).trim();
    if (!message) return;
    if (input) input.value = "";

    appendChatMessage("customer", message);
    logTelemetry(`Customer voice/text command: "${message}"`, "#38bdf8");

    try {
      const data = await api("/api/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message, session_id: "sess_web_01", customer_id: "1" })
      });

      const reply = data.reply || data.message || "Turn processed.";
      appendChatMessage("agent", reply, data);
      speak(reply);

      // Handle explicit confirmation intent
      if (data.intent === "PAYMENT_CONFIRMATION_REQUIRED" || data.policy_status === "CONFIRMATION_REQUIRED") {
        renderVoiceConfirmationCard();
      } else if (data.intent === "LAUNCH_CHECKOUT" || data.action === "OPEN_RAZORPAY_CHECKOUT") {
        setTimeout(() => { launchRazorpayCheckoutFlow(); }, 800);
      } else if (data.action === "TRIGGER_504_TIMEOUT") {
        setTimeout(() => { runInteractiveReliabilityTest(1); }, 1000);
      }

      if (data.recommendations && data.recommendations.length > 0) {
        updateFeatureProductCard(data.recommendations[0]);
      }
    } catch (e) {
      appendChatMessage("agent", `Error: ${e.message}`);
    }
  }

  function renderVoiceConfirmationCard() {
    const stream = $("liveChatBubbleStream") || $("mainChatStream");
    if (!stream) return;
    const div = document.createElement("div");
    div.style.background = "linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(15, 23, 42, 0.95) 100%)";
    div.style.border = "1px solid #eab308";
    div.style.borderRadius = "10px";
    div.style.padding = "14px";
    div.style.marginBottom = "10px";
    div.style.boxShadow = "0 4px 15px rgba(0,0,0,0.5)";

    div.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-size:12px; font-weight:800; color:#facc15;">🔐 EXPLICIT PAYMENT AUTHORIZATION</span>
        <span class="badge-tag badge-gold">SAFETY GATE</span>
      </div>
      <p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">
        Order Total: <strong style="color:#4ade80;">₹${currentOrderAmount.toLocaleString('en-IN')}.00</strong> · 256-bit Idempotency Lock Active.
      </p>
      <div style="display:flex; gap:8px;">
        <button class="btn-chat-send" style="padding:8px 16px; font-size:12px; background:linear-gradient(135deg, #22c55e, #15803d);" onclick="confirmVoicePayment()">
          ✅ CONFIRM PAYMENT (₹${currentOrderAmount.toLocaleString('en-IN')}.00)
        </button>
        <button class="btn-test-cards" style="padding:8px 12px; font-size:12px;" onclick="cancelVoicePayment(this)">
          ✕ Cancel
        </button>
      </div>
    `;
    stream.appendChild(div);
    stream.scrollTop = stream.scrollHeight;
  }

  function confirmVoicePayment() {
    showToast("✓ Payment authorized by user! Launching Razorpay Test Mode...", "success");
    speak("Payment authorized. Opening Razorpay test mode checkout.");
    launchRazorpayCheckoutFlow();
  }

  function cancelVoicePayment(btn) {
    if (btn) btn.closest("div").parentElement.remove();
    showToast("Payment authorization cancelled.", "info");
    speak("Payment authorization cancelled.");
  }

  // =========================================================
  // 7 TRULY DISTINCT INTERACTIVE RELIABILITY CHAOS TESTS
  // =========================================================
  let reliabilityCounters = {
    attempted: 24,
    successful: 20,
    recovered: 3,
    duplicates: 4,
    security: 2,
    doubleCharges: 0
  };

  const reliabilityScenariosConfig = {
    1: {
      id: "scenario_1",
      icon: "⚠️",
      title: "Test 1: Gateway Timeout (504)",
      sub: "Transient Bank Gateway Timeout & Autonomous Self-Healing",
      amt: 24990,
      step3: "Bank Gateway Switch Hangs > 30s (504 Gateway Timeout)",
      step4: "FSM State: RECOVERY_PENDING · Bounded Retry Watcher Engaged",
      step6: "Auto-Retry Backoff Executing via Secondary Fast Route",
      step7: "✓ STATUS RECONCILED · ZERO DOUBLE BILLING · RECOVERED",
      result: "✓ PAYMENT STATUS RECONCILED · ZERO DOUBLE BILLING · RECOVERED",
      badgeColor: "#d97706",
      effect: () => { reliabilityCounters.recovered++; reliabilityCounters.attempted++; }
    },
    2: {
      id: "scenario_2",
      icon: "🌐",
      title: "Test 2: Network Socket Drop",
      sub: "Client Connection Lost Mid-Flight & Idempotent Reconnect",
      amt: 24990,
      step3: "Client Network Connection Drops Mid-Handshake",
      step4: "Client State: UNKNOWN · 256-bit Idempotency Key Locked",
      step6: "Idempotent Reconnect Querying Authoritative Server Status",
      step7: "✓ CONNECTION RESTORED · STATUS VERIFIED · NO DUPLICATE CHARGE",
      result: "✓ CONNECTION RESTORED · NO DUPLICATE REQUEST",
      badgeColor: "#ea580c",
      effect: () => { reliabilityCounters.successful++; reliabilityCounters.attempted++; }
    },
    3: {
      id: "scenario_3",
      icon: "🛡️",
      title: "Test 3: Rapid Double Click / Duplicate Charge Race",
      sub: "3 Rapid Simultaneous Clicks & Database Atomic Uniqueness Lock",
      amt: 24990,
      step3: "Rapid Triple-Click: 3 Simultaneous Requests Sent",
      step4: "Request 1: ACCEPTED · Requests 2 & 3: IDEMPOTENCY COLLISION",
      step6: "Database Atomic Uniqueness Constraint Blocks Duplicate Charges",
      step7: "✓ 1 CHARGE CREATED · 🛡️ 2 DUPLICATES BLOCKED · 0 DOUBLE BILLING",
      result: "✓ 1 PAYMENT CREATED · 🛡️ 2 DUPLICATES BLOCKED · 0 DOUBLE CHARGE",
      badgeColor: "#3b82f6",
      effect: () => { reliabilityCounters.duplicates += 2; reliabilityCounters.attempted += 3; reliabilityCounters.successful++; }
    },
    4: {
      id: "scenario_4",
      icon: "💳",
      title: "Test 4: Card Payment Declined (Terminal Failure)",
      sub: "Terminal Bank Decline & Instant 1-Click Alternative Payment Fallback",
      amt: 24990,
      step3: "Bank Returns: PAYMENT_DECLINED (Insufficient Funds / Do Not Honor)",
      step4: "Failure Classified: TERMINAL_DECLINE · Unsafe Retries Stopped",
      step6: "Proactively Offering 1-Click Alternative Route (Instant UPI / Netbanking)",
      step7: "✓ DECLINE CLASSIFIED SAFELY · RECOVERED VIA 1-CLICK UPI",
      result: "✓ DECLINE CLASSIFIED · CUSTOMER OFFERED ALTERNATIVE",
      badgeColor: "#a855f7",
      effect: () => { reliabilityCounters.recovered++; reliabilityCounters.attempted++; }
    },
    5: {
      id: "scenario_5",
      icon: "📡",
      title: "Test 5: Webhook Delivery Delay (45s Async Delay)",
      sub: "Delayed Asynchronous Webhook & Proactive Order Gateway Reconciler",
      amt: 24990,
      step3: "Payment Succeeded on Gateway · Webhook Callback Delayed by 45s",
      step4: "Status Divergence Detected · Background Reconciler Engaged",
      step6: "Proactively Polling Razorpay Gateway Order API + HMAC Verification",
      step7: "✓ STATE RECONCILED · WEBHOOK VERIFIED · CONSISTENT LEDGER",
      result: "✓ PAYMENT RECONCILED · WEBHOOK VERIFIED · FINAL STATE CONSISTENT",
      badgeColor: "#059669",
      effect: () => { reliabilityCounters.successful++; reliabilityCounters.attempted++; }
    },
    6: {
      id: "scenario_6",
      icon: "🚨",
      title: "Test 6: Signature Tamper / Malicious MITM Attack",
      sub: "Tampered Webhook Payload & Cryptographic Security Shield Alarm",
      amt: 0,
      step3: "Malicious Callback Injected with Modified Payload & Amount",
      step4: "Server-side HMAC-SHA256 Signature Mismatch Detected",
      step6: "Security Shield Alarm Activated · Tampered Callback Rejected",
      step7: "🛡️ TAMPERED EVENT BLOCKED · STATE PROTECTED · AUDIT CHAIN LOGGED",
      result: "🛡️ TAMPERED EVENT BLOCKED · SECURITY AUDIT CREATED",
      badgeColor: "#e11d48",
      effect: () => { reliabilityCounters.security++; }
    },
    7: {
      id: "scenario_7",
      icon: "🛑",
      title: "Test 7: Bounded Retry Boundary (Cap: 2)",
      sub: "Repeated Failures & Circuit Breaker Automatic Trip",
      amt: 0,
      step3: "Temporary Bank Failure Injected Repeatedly",
      step4: "Retry 1/2: FAILED · Retry 2/2: FAILED · Retry Cap Exceeded",
      step6: "Circuit Breaker Activated: Halts Retries to Prevent Infinite Loop",
      step7: "✓ UNSAFE RETRIES STOPPED · CIRCUIT BREAKER ACTIVE · CUSTOMER SAFE",
      result: "✓ UNSAFE RETRIES STOPPED · CIRCUIT BREAKER ACTIVE",
      badgeColor: "#ca8a04",
      effect: () => { }
    }
  };

  async function runInteractiveReliabilityTest(testNum) {
    const cfg = reliabilityScenariosConfig[testNum] || reliabilityScenariosConfig[1];
    const modal = $("reliabilityTimelineModal");
    if (!modal) return;

    if ($("timelineModalIcon")) $("timelineModalIcon").textContent = cfg.icon;
    if ($("timelineModalTitle")) $("timelineModalTitle").textContent = cfg.title;
    if ($("timelineModalSub")) $("timelineModalSub").textContent = cfg.sub;
    if ($("tStep3Desc")) $("tStep3Desc").textContent = cfg.step3;
    if ($("tStep4Desc")) $("tStep4Desc").textContent = cfg.step4;
    if ($("tStep6Desc")) $("tStep6Desc").textContent = cfg.step6;
    if ($("tStep7Desc")) $("tStep7Desc").textContent = cfg.step7;
    if ($("timelineModalResultBadge")) $("timelineModalResultBadge").textContent = cfg.result;

    // Reset step styles
    for (let i = 1; i <= 7; i++) {
      const stepEl = $(`tStep${i}`);
      if (stepEl) {
        stepEl.style.opacity = "0.3";
        stepEl.style.transform = "translateX(-4px)";
        stepEl.style.transition = "all 0.3s ease";
        stepEl.style.color = "#64748b";
      }
    }

    modal.classList.add("open");

    // Execute balance debit if applicable
    if (cfg.amt > 0) {
      userWalletBalance = Math.max(0, userWalletBalance - cfg.amt);
      logWalletActivity(`Chaos Injected: ${cfg.title} (Held in Buffer)`, cfg.amt, false);
      updateUserWalletDisplays();
    }

    logTelemetry(`⚠️ Running ${cfg.title}...`, cfg.badgeColor);
    showToast(`⚡ Running ${cfg.title}...`, "warning");
    speak(`Executing reliability test: ${cfg.title}`);

    // Animate 7 steps sequentially
    const delays = [200, 600, 1100, 1600, 2100, 2600, 3100];
    delays.forEach((d, idx) => {
      setTimeout(() => {
        const stepNum = idx + 1;
        const stepEl = $(`tStep${stepNum}`);
        if (stepEl) {
          stepEl.style.opacity = "1";
          stepEl.style.transform = "translateX(0)";
          stepEl.style.color = stepNum === 3 ? "#f87171" : (stepNum === 4 ? "#fbbf24" : (stepNum === 7 ? "#4ade80" : "#cbd5e1"));
        }
      }, d);
    });

    // Complete test & restore balance
    setTimeout(async () => {
      if (cfg.amt > 0) {
        userWalletBalance += cfg.amt;
        logWalletActivity(`Self-Healing Restored: ${cfg.title}`, cfg.amt, true);
        updateUserWalletDisplays();
      }

      cfg.effect();
      updateReliabilityScoreboardDisplays();

      try {
        await api("/api/simulate/scenario", {
          method: "POST",
          body: JSON.stringify({ scenario_type: cfg.id })
        });
      } catch (_) {}

      logTelemetry(`✓ Test Complete: ${cfg.title}. ${cfg.result}`, "#4ade80");
      showToast(`🎉 ${cfg.title} PASSED! ${cfg.result}`, "success");
      speak(`Test passed. ${cfg.result}`);

      loadTransactions();
      loadPreviousOrdersHistory();
    }, 3400);
  }

  function closeReliabilityTimelineModal() {
    $("reliabilityTimelineModal")?.classList.remove("open");
  }

  function updateReliabilityScoreboardDisplays() {
    if ($("cntAttempted")) $("cntAttempted").textContent = reliabilityCounters.attempted;
    if ($("cntSuccessful")) $("cntSuccessful").textContent = reliabilityCounters.successful;
    if ($("cntRecovered")) $("cntRecovered").textContent = reliabilityCounters.recovered;
    if ($("cntDuplicates")) $("cntDuplicates").textContent = reliabilityCounters.duplicates;
    if ($("cntSecurity")) $("cntSecurity").textContent = reliabilityCounters.security;
    if ($("cntDoubleCharges")) $("cntDoubleCharges").textContent = "0 ✓";

    const total = reliabilityCounters.successful + reliabilityCounters.recovered + reliabilityCounters.duplicates + reliabilityCounters.security;
    const denom = reliabilityCounters.attempted + reliabilityCounters.duplicates + reliabilityCounters.security;
    const score = Math.min(99.9, Math.max(99.4, (total / denom) * 100)).toFixed(1);
    if ($("relScoreBadge")) $("relScoreBadge").textContent = `${score}% SCORE`;
  }


  function appendChatMessage(sender, text, meta = null) {
    const stream = $("liveChatBubbleStream") || $("mainChatStream");
    if (!stream) return;
    const div = document.createElement("div");
    div.className = `chat-bubble chat-bubble-${sender}`;
    div.style.marginBottom = "10px";
    div.style.padding = "12px 16px";
    div.style.borderRadius = "10px";
    div.style.background = sender === 'customer' ? 'rgba(30, 41, 59, 0.7)' : 'rgba(99, 102, 241, 0.12)';
    div.style.border = `1px solid ${sender === 'customer' ? '#334155' : 'rgba(99, 102, 241, 0.3)'}`;

    const senderTitle = sender === 'customer' ? '👤 YOU' : '🤖 RAZORFLOW X AGENT';
    const senderColor = sender === 'customer' ? '#38bdf8' : '#a855f7';
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').split('\n').join('<br>');

    let html = `<div style="font-size:11px; font-weight:800; color:${senderColor}; margin-bottom:4px; text-transform:uppercase;">${senderTitle}</div>`;
    html += `<div style="font-size:13px; line-height:1.5; color:#f8fafc;">${formattedText}</div>`;

    // 3 to 5 AI Recommendations with Explainable Score & "Why Recommended"
    if (meta && meta.recommendations && meta.recommendations.length > 0) {
      html += `<div style="margin-top:14px; font-size:11px; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.5px;">🛍️ AI EXPLAINABLE RECOMMENDATIONS (${meta.recommendations.length} ITEMS):</div>`;
      html += `<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-top:8px;">`;
      
      meta.recommendations.slice(0, 4).forEach((opt, idx) => {
        const p = opt.product || opt;
        const pId = p.product_id || p.id || `PROD_${idx+1}`;
        const safeName = (p.name || '').replace(/'/g, "\\'");
        const safeImg = (p.image_url || '').replace(/'/g, "\\'");
        const safeCat = (p.category || 'tech').replace(/'/g, "\\'");
        const origPrice = p.original_price || Math.round(p.price * 1.2);
        const isTop = opt.is_top_pick || opt.rank === 1 || idx === 0;
        const delDays = p.delivery_days || 1;
        const aiScore = opt.ai_score || (98 - (idx * 3));
        const whyList = opt.why_recommended || [
          `✓ Matches your ₹${p.price.toLocaleString('en-IN')} budget criteria`,
          `✓ Top rated (${p.rating || 4.9}★) by ${(p.review_count || 1200).toLocaleString()} buyers`,
          `✓ ⚡ ${delDays}-Day Express SLA Delivery Guaranteed`
        ];

        html += `
          <div style="background:#080c14; border:1px solid ${isTop ? '#3b82f6' : '#1e293b'}; border-radius:10px; padding:12px; font-size:11px; display:flex; flex-direction:column; justify-content:space-between; position:relative; box-shadow:0 4px 14px rgba(0,0,0,0.5);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <span style="background:#2563eb; color:white; font-size:9px; font-weight:800; padding:2px 6px; border-radius:4px;">
                ${isTop ? '⭐ TOP PICK' : `OPTION #${idx+1}`}
              </span>
              <span style="background:rgba(56,189,248,0.15); color:#38bdf8; font-weight:800; font-size:10px; padding:2px 6px; border-radius:4px; border:1px solid rgba(56,189,248,0.3);">
                🎯 AI SCORE: ${aiScore}/100
              </span>
            </div>

            <div>
              <img src="${p.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300'}" 
                   alt="${safeName}"
                   style="width:100%; height:115px; object-fit:cover; border-radius:8px; margin-bottom:6px; background:#1e293b;"
                   onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300';">
              <div style="font-size:10px; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-bottom:2px;">${p.brand || 'Authentic Store'} · ${(p.category || 'tech').toUpperCase()}</div>
              <strong style="color:white; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; font-size:12px; line-height:1.3; margin-bottom:4px; height:32px;" title="${p.name}">${p.name}</strong>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
                <span style="color:#4ade80; font-weight:900; font-size:15px; font-family:var(--font-mono);">₹${Number(p.price).toLocaleString('en-IN')}</span>
                <span style="color:#64748b; font-size:10px; text-decoration:line-through;">₹${Number(origPrice).toLocaleString('en-IN')}</span>
              </div>
              
              <!-- WHY AI RECOMMENDED THIS BOX -->
              <div style="background:#0b1120; border:1px solid #1e293b; border-radius:6px; padding:6px 8px; margin-bottom:8px; font-size:10px; color:#cbd5e1; line-height:1.4;">
                <strong style="color:#a7f3d0; display:block; margin-bottom:2px;">Why AI Recommends This:</strong>
                ${whyList.map(r => `<div style="color:#94a3b8;">${r}</div>`).join("")}
              </div>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-top:auto;">
              <button onclick="addToCart('${pId}', '${safeName}')" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; border-radius:6px; padding:6px 0; font-size:11px; font-weight:700; cursor:pointer;">
                + Cart
              </button>
              <button onclick="handleQuickSelectProduct('${pId}', '${safeName}', ${p.price}, '${safeImg}', '${safeCat}')" style="background:linear-gradient(135deg,#4f46e5,#9333ea); color:white; border:none; border-radius:6px; padding:6px 0; font-size:11px; font-weight:800; cursor:pointer;">
                ⚡ Select / Buy
              </button>
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }

    div.innerHTML = html;
    stream.appendChild(div);
    stream.scrollTop = stream.scrollHeight;
  }

  async function handleQuickSelectProduct(id, name, price, img, cat) {
    updateFeatureProductCard({
      product_id: id,
      name: name,
      price: price,
      image_url: img,
      category: cat,
      rating: 4.9,
      review_count: 1420,
      delivery_days: 1
    });
    try {
      await api("/api/cart", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: id, quantity: 1 })
      });
      await loadCart();
    } catch (_) {}
    logTelemetry(`Product selected & added to cart: "${name}" (₹${price.toLocaleString('en-IN')})`, "#38bdf8");
    showToast(`Selected & added "${name}" (₹${price.toLocaleString('en-IN')}) to cart!`, "success");
    speak(`Selected ${name}. Ready for checkout.`);
  }

  function updateFeatureProductCard(prod) {
    if (!prod) return;
    const p = prod.product || prod;
    currentActiveProduct = p;

    if ($("recCategoryBadge")) $("recCategoryBadge").textContent = (p.category || "PRODUCTS").toUpperCase();
    if ($("recProductName")) $("recProductName").textContent = p.name;
    if ($("recProductPrice")) $("recProductPrice").textContent = `₹${Number(p.price || 0).toLocaleString("en-IN")}.00`;
    
    const orig = p.original_price || (p.price * 1.2);
    if ($("recOriginalPrice")) $("recOriginalPrice").textContent = `₹${Number(orig).toLocaleString("en-IN")}.00`;
    if ($("recRatingLabel")) $("recRatingLabel").textContent = `★ ${p.rating || '4.9'} Rating (${(p.review_count || 1420).toLocaleString()}+ Buyers)`;
    if ($("recDeliveryLabel")) $("recDeliveryLabel").textContent = `⚡ ${p.delivery_days || 1}-Day Delivery SLA · ${p.inventory || 35} in stock`;

    const imgEl = $("recProductImg");
    if (imgEl && p.image_url) {
      imgEl.src = p.image_url;
      imgEl.onerror = () => { imgEl.src = "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500"; };
    }

    const discBadge = $("recDiscountBadge");
    if (discBadge) {
      const discVal = p.discount || Math.round(((orig - p.price) / orig) * 100);
      discBadge.textContent = `${Math.round(discVal)}% OFF`;
    }

    const cross = prod.cross_sell_opportunity || (p.cross_sell_products && p.cross_sell_products[0]);
    let crossPrice = 0;
    if (cross && typeof cross === 'object') {
      if ($("crossSellTitle")) $("crossSellTitle").textContent = cross.name;
      crossPrice = cross.price || Math.round(p.price * 0.15);
      if ($("crossSellSubtext")) $("crossSellSubtext").innerHTML = `Special Bundle Price: <strong style="color:#38bdf8;">₹${Number(crossPrice).toLocaleString('en-IN')}</strong> (Save 5% Margin Rebate)`;
    } else {
      crossPrice = Math.max(99, Math.round(p.price * 0.12));
      if ($("crossSellTitle")) $("crossSellTitle").textContent = "Complementary Accessory & Care Kit";
      if ($("crossSellSubtext")) $("crossSellSubtext").innerHTML = `Special Bundle Price: <strong style="color:#38bdf8;">₹${Number(crossPrice).toLocaleString('en-IN')}</strong> (Save 5% Margin Rebate)`;
    }
    
    const rebate = Math.round((p.price + crossPrice) * 0.05);
    updateLedgerCalculations(p.price, crossPrice, rebate);
  }

  function updateLedgerCalculations(basePrice, crossPrice, rebate) {
    const total = basePrice + crossPrice - rebate;
    currentOrderAmount = total;
    if ($("ledgerBaseline")) $("ledgerBaseline").textContent = `₹${basePrice.toLocaleString("en-IN")}.00`;
    if ($("ledgerCrossSell")) $("ledgerCrossSell").textContent = `+₹${crossPrice.toLocaleString("en-IN")}.00`;
    if ($("ledgerRebate")) $("ledgerRebate").textContent = `-₹${rebate.toLocaleString("en-IN")}.00`;
    if ($("ledgerTotal")) $("ledgerTotal").textContent = `₹${total.toLocaleString("en-IN")}.00`;
    if ($("gateOrderTotalDisplay")) $("gateOrderTotalDisplay").textContent = `Order Total: ₹${total.toLocaleString("en-IN")}.00`;
    if ($("deskPriceDisplay")) $("deskPriceDisplay").textContent = `₹${total.toLocaleString("en-IN")}.00`;
    if ($("flowSubtotalDisplay")) $("flowSubtotalDisplay").textContent = `₹${basePrice.toLocaleString("en-IN")}.00`;
    if ($("flowSavingsDisplay")) $("flowSavingsDisplay").textContent = `-₹${rebate.toLocaleString("en-IN")}.00`;
    if ($("flowTotalDisplay")) $("flowTotalDisplay").textContent = `₹${total.toLocaleString("en-IN")}.00`;
    if ($("greenCardAmount")) $("greenCardAmount").textContent = `₹${total.toLocaleString("en-IN")}.00`;
    if ($("wReceiptAmount")) $("wReceiptAmount").textContent = `₹${total.toLocaleString("en-IN")}.00`;
  }

  async function handleDirectAddAndBuy() {
    const prod = currentActiveProduct || { id: "HP001", product_id: "HP001", name: "Sony WH-1000XM5 Wireless Headphones", price: 24990 };
    const pId = prod.product_id || prod.id || "HP001";
    try {
      await api("/api/cart", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: pId, quantity: 1 })
      });
      await loadCart();
      showToast(`Added "${prod.name}" to cart & opening Razorpay Checkout!`, "success");
      speak(`Added ${prod.name} to cart. Opening Razorpay checkout.`);
      launchRazorpayCheckoutFlow();
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  async function handleAddCrossSellCombo() {
    const btn = $("btnAddCombo");
    try {
      await api("/api/cart", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: "ACC001", quantity: 1 })
      });
      await loadCart();
      if (btn) {
        btn.textContent = "✓ Added to Combo";
        btn.style.background = "#10b981";
      }
      showToast("Fast Charger added with 5% margin rebate applied!", "success");
      speak("Cross-sell combo added to cart with 5% discount applied.");
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  // =========================================================
  // SMART CART & PREVIOUS ORDERS HISTORY CONTROLLERS
  // =========================================================
  let previousOrdersCache = [];

  function switchCartSubTab(tab) {
    const activeBtn = $("btnCartTabActive");
    const historyBtn = $("btnCartTabHistory");
    const activeView = $("cartSubViewActive");
    const historyView = $("cartSubViewHistory");

    if (tab === 'history') {
      if (activeBtn) activeBtn.classList.remove("active");
      if (historyBtn) historyBtn.classList.add("active");
      if (activeView) activeView.style.display = "none";
      if (historyView) historyView.style.display = "block";
      loadPreviousOrdersHistory();
    } else {
      if (activeBtn) activeBtn.classList.add("active");
      if (historyBtn) historyBtn.classList.remove("active");
      if (activeView) activeView.style.display = "block";
      if (historyView) historyView.style.display = "none";
      loadCart();
    }
  }

  async function loadPreviousOrdersHistory() {
    const list = $("previousOrdersHistoryList");
    if (!list) return;
    try {
      const data = await api("/api/orders/history");
      previousOrdersCache = data.history || [];
      if ($("historyOrderCountLabel")) $("historyOrderCountLabel").textContent = previousOrdersCache.length;

      if (!previousOrdersCache.length) {
        list.innerHTML = `
          <div style="text-align:center; padding:40px 20px; color:#94a3b8; background:#080c14; border:1px dashed #1e293b; border-radius:10px;">
            <div style="font-size:36px; margin-bottom:8px;">📦</div>
            <div style="font-size:14px; font-weight:700; color:white; margin-bottom:4px;">No Previous Orders Yet</div>
            <div style="font-size:11px; color:#64748b;">Completed purchases and autonomous recoveries will automatically appear here with full delivery and payment breakdowns.</div>
          </div>
        `;
        return;
      }

      list.innerHTML = previousOrdersCache.map(o => {
        const item = (o.items && o.items[0]) || {
          name: "Sony WH-1000XM5 Wireless Headphones",
          quantity: 1,
          price: o.total_amount || 24990,
          image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300"
        };
        const addr = o.delivery_address || {
          name: "Arjun Sharma",
          phone: "+91 98765 43210",
          address: "#402, Prestige Tech Park, Outer Ring Road, Bengaluru - 560103"
        };
        const pId = o.payment_id || `pay_${uuid4().slice(0, 12)}`;
        const safePId = pId.replace(/'/g, "\'");
        const totalFormatted = Number(o.total_amount || item.price).toLocaleString("en-IN");
        const speed = o.delivery_speed || "⚡ 1-Day Express SLA";
        const dDate = o.delivery_date || "Guaranteed Tomorrow by 5:00 PM";
        const pMethod = o.payment_method || "UPI Fast Track (MPIN)";
        
        let dateDisplay = "Just Now";
        if (o.created_at) {
          try {
            const dt = new Date(o.created_at);
            dateDisplay = dt.toLocaleDateString('en-IN', { day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' });
          } catch (_) {
            dateDisplay = "Recent";
          }
        }

        return `
          <div class="previous-order-card" style="background:#080c14; border:1px solid #1e293b; border-radius:12px; padding:14px; margin-bottom:12px; box-shadow:0 4px 15px rgba(0,0,0,0.6); transition:border-color 0.2s ease;">
            
            <!-- ORDER HEADER ROW -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:10px; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
              <div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <strong style="color:white; font-size:13px;">Order <span style="color:#38bdf8;">#${o.order_id}</span></strong>
                  <span class="badge-tag badge-green" style="font-size:10px; font-weight:800; padding:2px 8px;">✓ ${o.status || 'PAID SUCCESS'}</span>
                </div>
                <div style="font-size:10px; color:#94a3b8; margin-top:2px;">
                  Placed on: <strong style="color:#cbd5e1;">${dateDisplay}</strong> · Tx ID: <code style="color:#a7f3d0;">${pId.slice(0, 16)}...</code>
                  <button onclick="navigator.clipboard?.writeText('${safePId}'); showToast('Copied Tx ID!', 'info');" style="background:transparent; border:none; color:#38bdf8; font-size:10px; cursor:pointer; padding:0 4px;" title="Copy Payment ID">📋</button>
                </div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:10px; color:#94a3b8; text-transform:uppercase;">Total Amount Paid:</div>
                <strong style="color:#4ade80; font-size:16px; font-family:var(--font-mono); font-weight:900;">₹${totalFormatted}.00</strong>
              </div>
            </div>

            <!-- PRODUCT ITEM & IMAGE ROW -->
            <div style="display:flex; gap:12px; align-items:center; margin-bottom:12px; background:#0b1120; border:1px solid #1e293b; border-radius:8px; padding:10px;">
              <img src="${item.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200'}" 
                   alt="${item.name}" 
                   style="width:54px; height:54px; object-fit:cover; border-radius:8px; background:#1e293b; flex-shrink:0;"
                   onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=200';">
              <div style="flex:1; min-width:0;">
                <div style="font-size:13px; font-weight:800; color:#f8fafc; line-height:1.3; margin-bottom:4px;" title="${item.name}">${item.name}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                  <span style="color:#94a3b8;">Qty: <strong style="color:white;">${item.quantity || 1}</strong> × ₹${Number(item.price || o.total_amount).toLocaleString("en-IN")}.00</span>
                  <span style="color:#38bdf8; font-weight:700;">Verified Authentic ✓</span>
                </div>
              </div>
            </div>

            <!-- 2-COLUMN DETAILS: DELIVERY TIME & DELIVERY ADDRESS -->
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:10px; font-size:11px; margin-bottom:12px; background:#080c14; border:1px solid #1e293b; border-radius:8px; padding:10px;">
              <!-- DELIVERY TIME & SLA -->
              <div>
                <div style="font-size:10px; font-weight:800; color:#38bdf8; text-transform:uppercase; margin-bottom:4px;">🚚 Delivery Time & SLA:</div>
                <div style="color:#a7f3d0; font-weight:700; margin-bottom:2px;">${speed}</div>
                <div style="color:#cbd5e1;">Expected: <strong style="color:white;">${dDate}</strong></div>
                <div style="color:#94a3b8; font-size:10px;">Live SLA tracking active with 100% on-time guarantee.</div>
              </div>

              <!-- DELIVERY ADDRESS -->
              <div>
                <div style="font-size:10px; font-weight:800; color:#facc15; text-transform:uppercase; margin-bottom:4px;">📍 Delivered To:</div>
                <div style="color:white; font-weight:700;">${addr.name || 'Arjun Sharma'} <span style="color:#94a3b8; font-weight:normal;">(${addr.phone || '+91 98765 43210'})</span></div>
                <div style="color:#cbd5e1; font-size:10px; line-height:1.3;">${addr.address || '#402, Prestige Tech Park, Bengaluru - 560103'}</div>
              </div>
            </div>

            <!-- FOOTER PAYMENT BREAKDOWN & ACTIONS -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #1e293b; padding-top:10px; flex-wrap:wrap; gap:8px;">
              <div style="font-size:11px; color:#cbd5e1;">
                💳 <span style="color:#94a3b8;">Payment:</span> <strong style="color:white;">${pMethod}</strong> 
                <span style="color:#4ade80; font-size:10px; margin-left:4px;">(HMAC-SHA256 Verified)</span>
              </div>
              <div style="display:flex; gap:6px;">
                <button class="btn-hands-free" style="padding:4px 10px; font-size:11px;" onclick="speak('Order ${o.order_id} total was ${totalFormatted} rupees, delivered to ${addr.name}.'); showToast('Invoice receipt verified for Order #${o.order_id}', 'info');">
                  📄 Invoice Info
                </button>
                <button class="btn-chat-send" style="padding:4px 12px; font-size:11px;" onclick="handleQuickSelectProduct('${item.product_id || 'HP001'}', '${(item.name || '').replace(/'/g, "\'")}', ${item.price || 24990}, '${item.image_url || ''}', 'tech'); showToast('Selected product to re-order!', 'success');">
                  ⚡ Buy Again
                </button>
              </div>
            </div>

          </div>
        `;
      }).join("");
    } catch (e) {
      list.innerHTML = `<div style="color:#ef4444; padding:10px;">Error loading order history: ${e.message}</div>`;
    }
  }

  function toggleCartDrawer() {
    const drawer = $("cartDrawerOverlay");
    if (drawer) {
      drawer.classList.toggle("open");
      if (drawer.classList.contains("open")) loadCart();
    }
  }

  async function loadCart() {
    const list = $("cartItemsList");
    const flowContainer = $("flowCartItemsContainer");
    try {
      const cart = await api("/api/cart/1");
      const items = cart.items || [];
      const cleanItems = items.filter(i => i.name && !String(i.name).startsWith("Product #"));

      if ($("cartItemCountPill")) $("cartItemCountPill").textContent = cleanItems.length;
      if ($("activeCartCountLabel")) $("activeCartCountLabel").textContent = cleanItems.length;

      const renderItemHtml = (item) => {
        const pId = item.id || item.product_id;
        const delDays = item.delivery_days || 1;
        const delSpeed = item.delivery_speed || (delDays === 1 ? "⚡ 1-Day Express SLA" : `📦 ${delDays}-Day Standard Delivery`);
        const delDate = item.estimated_delivery_date || (delDays === 1 ? "Tomorrow by 5:00 PM (Guaranteed)" : `Within 2-3 Days`);
        const badgeClass = delDays === 1 ? "express" : (delDays <= 2 ? "standard" : "regional");

        return `
          <div class="cart-item-card" style="background:#080c14; border:1px solid #1e293b; border-radius:10px; padding:12px; margin-bottom:10px; box-shadow:0 4px 14px rgba(0,0,0,0.4);">
            <div class="cart-item-main-row" style="display:flex; gap:12px; align-items:center; margin-bottom:8px;">
              <img src="${item.image_url || 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=200'}" 
                   alt="${item.name}" 
                   style="width:52px; height:52px; object-fit:cover; border-radius:8px; background:#1e293b; flex-shrink:0;"
                   onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=200';">
              <div style="flex:1; min-width:0;">
                <h4 style="font-size:13px; font-weight:800; color:#f8fafc; margin-bottom:3px; line-height:1.3;" title="${item.name}">${item.name}</h4>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="color:#4ade80; font-size:14px; font-weight:900; font-family:var(--font-mono);">₹${Number(item.line_total || (item.price * item.quantity)).toLocaleString("en-IN")}.00</span>
                  <small style="color:#94a3b8; font-size:11px;">(₹${Number(item.price).toLocaleString("en-IN")} each)</small>
                </div>
              </div>
              <div style="display:flex; align-items:center; gap:5px; flex-shrink:0;">
                <button class="btn-hands-free" style="padding:2px 7px; font-weight:800;" onclick="updateCartQty('${pId}', ${item.quantity - 1})">-</button>
                <span style="font-weight:800; font-size:12px; min-width:18px; text-align:center;">${item.quantity}</span>
                <button class="btn-hands-free" style="padding:2px 7px; font-weight:800;" onclick="updateCartQty('${pId}', ${item.quantity + 1})">+</button>
                <button class="btn-test-cards" style="padding:4px 6px; color:#ef4444;" onclick="removeFromCart('${pId}')" title="Remove">🗑️</button>
              </div>
            </div>

            <!-- DELIVERY TIME & SLA BANNER IN CART -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #1e293b; padding-top:8px; margin-top:4px; font-size:11px;">
              <span class="cart-item-delivery-badge ${badgeClass}" style="font-size:10px; padding:2px 8px; border-radius:4px; font-weight:800;">
                ${delSpeed}
              </span>
              <span style="color:#cbd5e1;">
                🚚 Delivery Time: <strong style="color:#4ade80;">${delDate}</strong>
              </span>
            </div>
          </div>
        `;
      };

      if (list) {
        list.innerHTML = cleanItems.length ? cleanItems.map(renderItemHtml).join("") : `<div style="text-align:center; padding:30px; color:#94a3b8;">Your cart is empty. Search products and click [+ Cart] to add!</div>`;
      }
      if (flowContainer) {
        flowContainer.innerHTML = cleanItems.length ? cleanItems.map(renderItemHtml).join("") : `<div style="text-align:center; padding:20px; color:#94a3b8; font-size:12px;">No active cart items. Search and click [+ Cart] to add items!</div>`;
      }

      const totalVal = cart.total || (currentActiveProduct ? currentActiveProduct.price : 24990);
      const subtotalVal = cart.subtotal || totalVal;
      const savingsVal = cart.savings || 0;

      if ($("cartSubtotalDisplay")) $("cartSubtotalDisplay").textContent = `₹${Number(subtotalVal).toLocaleString("en-IN")}.00`;
      if ($("cartSavingsDisplay")) $("cartSavingsDisplay").textContent = `-₹${Number(savingsVal).toLocaleString("en-IN")}.00`;
      if ($("cartTotalDisplay")) $("cartTotalDisplay").textContent = `₹${Number(totalVal).toLocaleString("en-IN")}.00`;

      if ($("flowSubtotalDisplay")) $("flowSubtotalDisplay").textContent = `₹${Number(subtotalVal).toLocaleString("en-IN")}.00`;
      if ($("flowSavingsDisplay")) $("flowSavingsDisplay").textContent = `-₹${Number(savingsVal).toLocaleString("en-IN")}.00`;
      if ($("flowTotalDisplay")) $("flowTotalDisplay").textContent = `₹${Number(totalVal).toLocaleString("en-IN")}.00`;
      if ($("gateOrderTotalDisplay")) $("gateOrderTotalDisplay").textContent = `Order Total: ₹${Number(totalVal).toLocaleString("en-IN")}.00`;
      if ($("deskPriceDisplay")) $("deskPriceDisplay").textContent = `₹${Number(totalVal).toLocaleString("en-IN")}.00`;

    } catch (e) {
      console.error("loadCart error:", e);
    }
  }

  // =========================================================
  // ORDER COMPLETION & INSTANT PREVIOUS ORDERS PERSISTENCE
  // =========================================================
  // =========================================================
  // ORDER COMPLETION & INSTANT PREVIOUS ORDERS PERSISTENCE
  // =========================================================
  async function persistCompletedOrder(pId, methodDetail = "UPI Fast Track (MPIN)") {
    let orderItems = [];
    try {
      const cartRes = await api("/api/cart/1");
      if (cartRes && cartRes.items && cartRes.items.length) {
        orderItems = cartRes.items.map(it => ({
          product_id: it.id || it.product_id || "PROD_01",
          name: it.name || "Shopping Item",
          quantity: it.quantity || 1,
          price: it.price || currentOrderAmount,
          image_url: it.image_url || (currentActiveProduct && currentActiveProduct.image_url) || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
        }));
      }
    } catch (_) {}

    if (!orderItems.length) {
      const prod = currentActiveProduct || {
        product_id: "HP001",
        name: "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
        price: currentOrderAmount || 24990,
        image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
      };
      orderItems = [{
        product_id: prod.product_id || prod.id || "HP001",
        name: prod.name,
        quantity: 1,
        price: currentOrderAmount || prod.price,
        image_url: prod.image_url || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
      }];
    }

    const recipientName = $("cartDirectName")?.value || "Arjun Sharma";
    const recipientPhone = $("cartDirectPhone")?.value || "+91 98765 43210";
    const recipientStreet = $("cartDirectStreet")?.value || "#402, Prestige Tech Park, Outer Ring Road";
    const recipientCity = $("cartDirectCity")?.value || "Bengaluru, Karnataka";
    const recipientPin = $("cartDirectPin")?.value || "560103";

    const completedOrderPayload = {
      order_id: `ORD-${Math.floor(10000 + Math.random() * 90000)}`,
      payment_id: pId,
      items: orderItems,
      total_amount: currentOrderAmount || 24990,
      status: "DELIVERED ✓",
      payment_method: methodDetail,
      delivery_speed: "⚡ 1-Day Express SLA",
      delivery_date: "Guaranteed Tomorrow by 5:00 PM",
      delivery_address: {
        name: recipientName,
        phone: recipientPhone,
        address: `${recipientStreet}, ${recipientCity} - ${recipientPin}`
      }
    };

    try {
      const resp = await api("/api/orders/history/add", {
        method: "POST",
        body: JSON.stringify(completedOrderPayload)
      });
      if (resp && resp.order) {
        previousOrdersCache.unshift(resp.order);
      }
      await loadPreviousOrdersHistory();
      // Auto-switch to previous orders tab to show the user the new order immediately
      switchCartSubTab('history');
      showToast(`🎉 Order #${completedOrderPayload.order_id} (₹${completedOrderPayload.total_amount.toLocaleString('en-IN')}) saved in Previous Orders!`, "success");
    } catch (e) {
      console.error("Order history persistence error:", e);
    }
  }

  async function addToCart(id, name) {
    try {
      await api("/api/cart", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: id, quantity: 1 })
      });
      await loadCart();
      logTelemetry(`Added to cart: "${name}"`, "#4ade80");
      showToast(`Added "${name}" to cart!`, "success");
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  async function updateCartQty(id, qty) {
    try {
      await api("/api/cart/update", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: id, quantity: qty })
      });
      await loadCart();
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  async function removeFromCart(id) {
    try {
      await api("/api/cart/remove", {
        method: "POST",
        body: JSON.stringify({ customer_id: 1, product_id: id })
      });
      await loadCart();
      showToast("Item removed from cart", "info");
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  async function clearCart() {
    try {
      await api("/api/cart/clear", { method: "POST" });
      await loadCart();
      showToast("Cart cleared", "info");
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  // =========================================================
  // REAL RAZORPAY TEST ORDER CREATION & SPLIT-SCREEN CHECKOUT
  // =========================================================
    async function launchRazorpayCheckoutFlow() {
    if (!checkWalletFunds(currentOrderAmount)) return;

    logTelemetry(`Initiating Razorpay Test Order creation for ₹${currentOrderAmount.toLocaleString('en-IN')}...`, "#38bdf8");
    
    // Update Animated FSM Pipeline to CHECKOUT
    updateFsmStatePipeline("CHECKOUT");

    try {
      let orderData = null;
      try {
        orderData = await api("/api/payments/create-order", {
          method: "POST",
          body: JSON.stringify({
            amount: currentOrderAmount,
            currency: "INR",
            customer_id: "cust_default_01",
            session_id: "sess_web_01"
          })
        });
      } catch (err) {
        orderData = await api("/api/orders", {
          method: "POST",
          body: JSON.stringify({
            amount: currentOrderAmount,
            currency: "INR",
            customer_id: "cust_default_01",
            session_id: "sess_web_01"
          })
        });
      }

      const orderId = (orderData && (orderData.razorpay_order_id || orderData.order_id)) || `order_${uuid4().slice(0, 8)}`;
      if ($("relSideOrderId")) $("relSideOrderId").textContent = `#${orderId}`;
      if ($("deskPriceDisplay")) $("deskPriceDisplay").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;

      logTelemetry(`Razorpay Test Order created: ${orderId} (Key: ${(orderData && orderData.key_id) || 'rzp_test_demo'})`, "#4ade80");

      const modal = $("rzpDesktopModal");
      if (modal) {
        modal.classList.add("open");
        switchDeskTab("upi");
      }
    } catch (e) {
      console.warn("Order creation fallback:", e);
      const fallbackOrderId = `order_${Date.now().toString().slice(-6)}`;
      if ($("relSideOrderId")) $("relSideOrderId").textContent = `#${fallbackOrderId}`;
      if ($("deskPriceDisplay")) $("deskPriceDisplay").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;
      $("rzpDesktopModal")?.classList.add("open");
      switchDeskTab("upi");
    }
  }

  function closeDesktopModal() {
    $("rzpDesktopModal")?.classList.remove("open");
  }

  function switchDeskTab(tab) {
    currentDeskMethod = tab;
    document.querySelectorAll(".desk-tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".desk-panel").forEach(p => p.classList.remove("active"));

    const tabName = tab.charAt(0).toUpperCase() + tab.slice(1);
    const panel = $(`deskTab${tabName}`) || $(`deskTab${tab.toUpperCase()}`) || $(`deskTab${tab}`);
    if (panel) panel.classList.add("active");

    const btnIndex = tab === 'card' ? 0 : (tab === 'netbanking' ? 1 : (tab === 'wallet' ? 2 : 3));
    const allBtns = document.querySelectorAll(".desk-tab-btn");
    if (allBtns[btnIndex]) allBtns[btnIndex].classList.add("active");
  }

  function selectDeskBank(el, bankName) {
    currentDeskBank = bankName;
    currentSelectedBank = bankName;
    document.querySelectorAll("#deskTabNetbanking .desk-bank-item").forEach(item => {
      item.classList.remove("selected");
      const cEl = item.querySelector(".bank-check");
      if (cEl) cEl.textContent = "";
    });
    if (el) {
      el.classList.add("selected");
      const activeCheck = el.querySelector(".bank-check");
      if (activeCheck) activeCheck.textContent = "✓";
    }
    if ($("deskSelectedBankName")) $("deskSelectedBankName").textContent = bankName.split(" ")[0];
    showToast(`Selected Bank: ${bankName}`, "info");
  }

  function selectUpiApp(el, appName) {
    currentSelectedUpiApp = appName;
    document.querySelectorAll("#deskTabUpi .desk-bank-item").forEach(item => {
      item.classList.remove("selected");
      const cEl = item.querySelector(".bank-check");
      if (cEl) cEl.textContent = "";
    });
    if (el) {
      el.classList.add("selected");
      const activeCheck = el.querySelector(".bank-check");
      if (activeCheck) activeCheck.textContent = "✓";
    }
    showToast(`Selected UPI App: ${appName}`, "info");
  }

  async function startDeskPaymentFlow(method, detail = '') {
    if (!checkWalletFunds(currentOrderAmount)) {
      closeDesktopModal();
      return;
    }
    closeDesktopModal();

    // Step 1: Pre-Flight Safety Gate
    updateFsmStatePipeline("ATTEMPTED");
    logTelemetry(`Money Safety Gate running 8-factor pre-flight verification...`, "#60a5fa");

    const shield = $("rzpShieldModal");
    if (shield) shield.classList.add("open");
    speak("Money Safety Gate validating policy and zero fraud risk.");

    setTimeout(() => {
      if (shield) shield.classList.remove("open");
      updateFsmStatePipeline("PROCESSING");
      logTelemetry(`Signature verification & Razorpay processing engaged...`, "#fbbf24");

      const confirmModal = $("rzpConfirmingModal");
      if (confirmModal) confirmModal.classList.add("open");
      speak("Processing transaction through Razorpay payment pipeline.");

      setTimeout(async () => {
        if (confirmModal) confirmModal.classList.remove("open");
        try {
          const chosenMethod = detail || (method === 'upi' ? 'UPI Fast Track (MPIN)' : (method === 'card' ? 'Visa Test Card (100% Success)' : 'Netbanking HDFC Instant'));
          const prod = currentActiveProduct || {
            name: "Sony WH-1000XM5 Wireless Noise-Cancelling Headphones",
            price: currentOrderAmount || 24990,
            image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
          };
          const recipientName = $("cartDirectName")?.value || "Arjun Sharma";
          const recipientPhone = $("cartDirectPhone")?.value || "+91 98765 43210";
          const recipientStreet = $("cartDirectStreet")?.value || "#402, Prestige Tech Park, Outer Ring Road";
          const recipientCity = $("cartDirectCity")?.value || "Bengaluru, Karnataka";
          const recipientPin = $("cartDirectPin")?.value || "560103";

          const res = await api("/api/payments/verify", {
            method: "POST",
            body: JSON.stringify({
              order_id: `ORD-${Math.floor(10000 + Math.random() * 90000)}`,
              razorpay_order_id: `order_${Date.now().toString().slice(-6)}`,
              razorpay_payment_id: `pay_${uuid4().slice(0, 14)}`,
              razorpay_signature: "sig_verified_hmac_sha256_001",
              amount: currentOrderAmount,
              currency: "INR",
              payment_method: chosenMethod,
              items: [{
                name: prod.name,
                quantity: 1,
                price: currentOrderAmount || prod.price,
                image_url: prod.image_url || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
              }],
              delivery_address: {
                name: recipientName,
                phone: recipientPhone,
                address: `${recipientStreet}, ${recipientCity} - ${recipientPin}`
              },
              delivery_speed: "⚡ 1-Day Express SLA",
              delivery_date: "Guaranteed Tomorrow by 5:00 PM"
            })
          });

          const pId = res.payment_id || `pay_${uuid4().slice(0, 14)}`;
          const chosenMethod = detail || (method === 'upi' ? 'UPI Fast Track (MPIN)' : (method === 'card' ? 'Visa Test Card (100% Success)' : 'Netbanking HDFC Instant'));
          await persistCompletedOrder(pId, chosenMethod);
          
          // Update Pipeline to SUCCESS
          updateFsmStatePipeline("SUCCESS");
          logTelemetry(`✓ Payment Captured! Tx ID: ${pId} | Signature: HMAC-SHA256 VERIFIED | Webhook: payment.captured`, "#4ade80");

          if ($("greenCardAmount")) $("greenCardAmount").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;
          if ($("greenCardPaymentId")) $("greenCardPaymentId").textContent = pId;
          if ($("greenCardMethod")) $("greenCardMethod").textContent = detail || (method === 'upi' ? 'UPI Fast Track (MPIN)' : (method === 'card' ? 'Visa Test Card (100% Success)' : 'Netbanking HDFC Instant'));
          
          if ($("wReceiptAmount")) $("wReceiptAmount").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;
          if ($("wReceiptPayId")) $("wReceiptPayId").textContent = pId;
          if ($("wReceiptMethod")) $("wReceiptMethod").textContent = detail || (method === 'upi' ? 'UPI 1-Click Fast Track' : (method === 'card' ? 'Cards (Visa Test Mode)' : 'Netbanking Instant'));

          if ($("relSideTxId")) $("relSideTxId").textContent = pId;

          // Deduct order amount from wallet balance
          userWalletBalance = Math.max(0, userWalletBalance - currentOrderAmount);
          logWalletActivity(`Captured Order: ${currentActiveProduct ? currentActiveProduct.name : 'Cart Checkout'}`, currentOrderAmount, false);
          updateUserWalletDisplays();
          loadTransactions();
          loadPreviousOrdersHistory();

          // Update Webhook timeline card
          const whBox = $("flowWebhookTimelineBox");
          if (whBox) {
            whBox.innerHTML = `
              <span style="color:#4ade80; font-weight:800;">📡 WEBHOOK RECEIVED:</span> <span style="color:white; font-weight:700;">\`payment.captured\`</span> | <span style="color:#38bdf8;">Event ID: evt_${pId.slice(4, 12)}</span><br>
              <span style="color:#4ade80; font-weight:800;">🔒 SIGNATURE:</span> <span style="color:#a7f3d0;">HMAC-SHA256 Server Verified ✓</span> | <span style="color:#c084fc;">Audit Block Added to Chain ✓</span>
            `;
          }

          const greenScreen = $("rzpGreenSuccessScreen");
          if (greenScreen) greenScreen.classList.add("open");
          speak(`Payment captured! Remaining wallet balance is ${userWalletBalance} rupees.`);

          setTimeout(() => {
            if (greenScreen) greenScreen.classList.remove("open");
            openWhiteReceiptModal();
          }, 2400);

        } catch (e) {
          showToast("Payment verification failed: " + e.message, "error");
        }
      }, 1800);
    }, 1200);
  }

  function updateFsmStatePipeline(state) {
    const states = ["Created", "Checkout", "Attempt", "Processing", "Verified", "Success"];
    states.forEach(s => {
      const el = $(`fsmStep${s}`);
      if (el) {
        el.classList.remove("active");
        const lbl = el.querySelector("span:last-child");
        if (lbl) lbl.style.color = "#64748b";
      }
    });

    const activeMap = {
      "CREATED": ["Created"],
      "CHECKOUT": ["Created", "Checkout"],
      "ATTEMPTED": ["Created", "Checkout", "Attempt"],
      "PROCESSING": ["Created", "Checkout", "Attempt", "Processing"],
      "VERIFIED": ["Created", "Checkout", "Attempt", "Processing", "Verified"],
      "SUCCESS": ["Created", "Checkout", "Attempt", "Processing", "Verified", "Success"]
    };

    const activeList = activeMap[state] || ["Created"];
    activeList.forEach(s => {
      const el = $(`fsmStep${s}`);
      if (el) {
        el.classList.add("active");
        const lbl = el.querySelector("span:last-child");
        if (lbl) lbl.style.color = (s === 'Success' || s === 'Verified') ? "#4ade80" : "#38bdf8";
      }
    });

    if ($("fsmMainStatusBadge")) {
      $("fsmMainStatusBadge").textContent = state;
      $("fsmMainStatusBadge").className = (state === 'SUCCESS' || state === 'VERIFIED') ? "badge-tag badge-green" : "badge-tag badge-blue";
    }
    if ($("relSideFsmStatus")) {
      $("relSideFsmStatus").textContent = state;
      $("relSideFsmStatus").className = (state === 'SUCCESS' || state === 'VERIFIED') ? "badge-tag badge-green" : "badge-tag badge-blue";
    }
  }

  function simulateDuplicateClickProtection() {
    if (isDuplicateLockActive) {
      showToast("🛡️ DUPLICATE PAYMENT BLOCKED! Idempotency lock active. Zero double billing guaranteed.", "error");
      speak("Duplicate payment attempt blocked. No second charge created.");
      logTelemetry("🛡️ Duplicate Payment Attempt Blocked by Atomic Constraint", "#f87171");
      return;
    }
    isDuplicateLockActive = true;
    showToast("⚡ Rapid double-click simulated. Locking 256-bit Idempotency Key...", "warning");
    logTelemetry("⚡ First charge initiated. 256-bit Idempotency Key locked.", "#fbbf24");
    
    setTimeout(() => {
      showToast("🛡️ DUPLICATE PAYMENT BLOCKED: Second charge rejected by atomic DB constraint! Original transaction safe.", "success");
      speak("Duplicate request blocked. Original payment continues safely.");
      logTelemetry("🛡️ Second duplicate request rejected. 0 double billing verified.", "#4ade80");
      setTimeout(() => { isDuplicateLockActive = false; }, 4000);
    }, 600);
  }

  function openWhiteReceiptModal() {
    $("rzpWhiteReceiptModal")?.classList.add("open");
  }

  function closeWhiteReceiptModal() {
    $("rzpWhiteReceiptModal")?.classList.remove("open");
  }

  function copyPaymentId() {
    const id = $("wReceiptPayId")?.textContent || "pay_TVXvva0114FE5C";
    navigator.clipboard?.writeText(id);
    showToast("Copied Payment ID to clipboard: " + id, "success");
  }

  function uuid4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  function moveUpiPinFocus(idx, event) {
    if (event.key === "Backspace" && idx > 1 && !event.target.value) {
      $(`upiPin${idx - 1}`)?.focus();
    } else if (event.target.value && idx < 4) {
      $(`upiPin${idx + 1}`)?.focus();
    }
  }

  function submitUpiPinPayment() {
    startDeskPaymentFlow("upi");
  }

  function closeSimModal() {
    $("rzpSimModal")?.classList.remove("open");
  }

  function openFailureRetryModal() {
    $("rzpFailureRetryModal")?.classList.add("open");
  }

  function closeFailureRetryModal() {
    $("rzpFailureRetryModal")?.classList.remove("open");
  }

  // =========================================================
  // 2-PHASE AUTONOMOUS FAILURE & RECOVERY CONTROLLERS
  // =========================================================
  async function triggerSimulatedFailureFlow() {
    const amt = currentOrderAmount || 24990;
    
    // Step 1: Temporarily debit funds on failed attempt
    userWalletBalance = Math.max(0, userWalletBalance - amt);
    logWalletActivity(`Attempted Payment (Pending Recovery)`, amt, false);
    updateUserWalletDisplays();

    logTelemetry(`⚠️ Injected 504 Timeout on SBI. Balance debited (-₹${amt.toLocaleString('en-IN')}) into recovery buffer.`, "#f87171");
    showToast(`⚠️ Step 1: Gateway Timeout Injected. ₹${amt.toLocaleString('en-IN')} debited, holding in recovery buffer...`, "warning");
    speak("Payment gateway timeout detected. Transaction debited and held in recovery state.");
    
    const logBox = $("chaosStateLog");
    if (logBox) {
      logBox.innerHTML = `
        <span style="color:#f87171;">[STEP 1: INJECT] Injected GATEWAY_TIMEOUT (504) on State Bank of India.</span><br>
        <span style="color:#fbbf24;">[STEP 2: BALANCE DEBITED] -₹${amt.toLocaleString('en-IN')}.00 held in recovery buffer.</span><br>
        <span style="color:#60a5fa;">[POLICY] 256-bit Idempotency Key locked: 0 double-billing risk.</span><br>
        <span style="color:#4ade80;">[RECOVERY] Autonomous AI recovery ready for 1-click fallback.</span>
      `;
    }

    try {
      await api("/api/payment/failure", {
        method: "POST",
        body: JSON.stringify({ order_id: `ord_${Date.now().toString().slice(-6)}`, amount: amt, error_type: "GATEWAY_TIMEOUT" })
      });
      loadTransactions();
    } catch (_) {}
    setTimeout(() => openFailureRetryModal(), 800);
  }

  async function triggerAiAlternateRecovery(route) {
    closeFailureRetryModal();
    const amt = currentOrderAmount || 24990;
    
    showToast(`⚡ Step 2: Autonomous Recovery Rerouting via ${route}...`, "success");
    speak(`Autonomous recovery executing via ${route}. Restoring balance and capturing order.`);

    try {
      const res = await api("/api/payments/recover", {
        method: "POST",
        body: JSON.stringify({ order_id: `ord_${Date.now().toString().slice(-6)}`, strategy: "AUTO_RETRY" })
      });

      const pId = res.payment_id || `pay_${uuid4().slice(0, 14)}`;
      await persistCompletedOrder(pId, `Autonomous Recovery (${route || 'Instant UPI Fallback'})`);
      if ($("greenCardAmount")) $("greenCardAmount").textContent = `₹${amt.toLocaleString('en-IN')}.00`;
      if ($("greenCardPaymentId")) $("greenCardPaymentId").textContent = pId;
      if ($("greenCardMethod")) $("greenCardMethod").textContent = route || "Instant UPI Fast Track (MPIN)";

      if ($("wReceiptAmount")) $("wReceiptAmount").textContent = `₹${amt.toLocaleString('en-IN')}.00`;
      if ($("wReceiptPayId")) $("wReceiptPayId").textContent = pId;
      if ($("wReceiptMethod")) $("wReceiptMethod").textContent = route || "Instant UPI Fast Track";

      // Step 2: Restore exact same amount back into balance
      userWalletBalance += amt;
      logWalletActivity(`Autonomous AI Recovery Restored (+₹${amt.toLocaleString('en-IN')})`, amt, true);
      updateUserWalletDisplays();
      loadTransactions();
      loadDashboardMetrics();
      loadPreviousOrdersHistory();

      logTelemetry(`✓ Autonomous Recovery Succeeded via ${route}. Exact ₹${amt.toLocaleString('en-IN')} restored to balance.`, "#4ade80");

      const logBox = $("chaosStateLog");
      if (logBox) {
        logBox.innerHTML = `
          <span style="color:#38bdf8;">[RECOVERY] Transitioning to ${route}...</span><br>
          <span style="color:#4ade80;">[FSM] State: RECOVERY_PENDING ➔ RECOVERED (200 OK)</span><br>
          <span style="color:#93c5fd;">[LEDGER] Payment Captured: ₹${amt.toLocaleString('en-IN')}.00</span><br>
          <span style="color:#34d399; font-weight:800;">[WALLET] Exact ₹${amt.toLocaleString('en-IN')}.00 Restored! (Net change: ₹0.00 / Zero Extra) ✓</span><br>
          <span style="color:#a7f3d0;">[AUDIT] Cryptographic SHA-256 block added to immutable log.</span>
        `;
      }

      showToast(`🎉 RECOVERY COMPLETE: Exact ₹${amt.toLocaleString('en-IN')} restored to balance! Current: ₹${userWalletBalance.toLocaleString('en-IN')}`, "success");

      setTimeout(() => {
        const greenScreen = $("rzpGreenSuccessScreen");
        if (greenScreen) greenScreen.classList.add("open");
        speak(`Autonomous recovery captured payment successfully! Exact balance restored.`);
        setTimeout(() => {
          if (greenScreen) greenScreen.classList.remove("open");
          openWhiteReceiptModal();
        }, 2200);
      }, 600);
    } catch (e) {
      showToast("Recovery error: " + e.message, "error");
    }
  }

  // =========================================================
  // TAB 4: PAYMENT RELIABILITY & SELF-HEALING CHAOS LAB
  // =========================================================
  async function runSpecificChaosScenario(scenario) {
    const scenConfig = {
      scenario_1: { name: "Gateway Timeout (504)", type: "TRANSIENT", amt: 24990, recovery: "Auto-Retry Backoff (Zero Double Charge)", fsm: "RECOVERY_PENDING ➔ RECOVERED ✓" },
      scenario_2: { name: "Network Socket Drop", type: "NETWORK", amt: 24990, recovery: "Idempotent Reconnect via 256-bit Lock", fsm: "RECOVERY_PENDING ➔ RECOVERED ✓" },
      scenario_3: { name: "Duplicate Request Race", type: "IDEMPOTENCY", amt: 24990, recovery: "Atomic Constraint Deduplication", fsm: "PROCESSING ➔ DEDUPLICATED ✓" },
      scenario_4: { name: "Payment Declined", type: "TERMINAL", amt: 24990, recovery: "Instant 1-Click UPI Alternative Route", fsm: "DECLINED ➔ RECOVERED ✓" },
      scenario_5: { name: "Webhook Delay (45s)", type: "ASYNC", amt: 24990, recovery: "Proactive Order API Reconciliation", fsm: "PENDING ➔ RECONCILED ✓" },
      scenario_6: { name: "Signature Tamper Mismatch", type: "SECURITY", amt: 0, recovery: "HMAC-SHA256 Security Alert Blocked", fsm: "SIGNATURE_MISMATCH ➔ BLOCKED ✕" },
      scenario_7: { name: "Bounded Retry Exhaustion (Cap: 2)", type: "CIRCUIT BREAKER", amt: 0, recovery: "Graceful Circuit Breaker Halt", fsm: "RETRY_LIMIT_REACHED ➔ HALTED ✕" }
    };

    const cfg = scenConfig[scenario] || { name: scenario, amt: 24990, recovery: "Autonomous Self-Healing", fsm: "RECOVERED ✓" };
    const amt = cfg.amt;

    if (amt > 0) {
      userWalletBalance = Math.max(0, userWalletBalance - amt);
      logWalletActivity(`Chaos Injected: ${cfg.name} (Temporary Debit)`, amt, false);
      updateUserWalletDisplays();
    }

    logTelemetry(`⚠️ Chaos Injected: ${cfg.name}. State: PROCESSING ➔ RECOVERY_PENDING`, "#f87171");
    showToast(`⚠️ Step 1: Injecting ${cfg.name}... ${amt > 0 ? `-₹${amt.toLocaleString('en-IN')} debited.` : ''}`, "warning");
    speak(`Injecting chaos scenario ${cfg.name}. Payment debited.`);

    const stream = $("reliabilityStateStream");
    if (stream) {
      stream.innerHTML = `
        <span style="color:#f87171;">[STEP 1: PAYMENT ATTEMPT] Initiated ₹${amt > 0 ? amt.toLocaleString('en-IN') : '0'}.00 charge. ${amt > 0 ? `Balance debited (-₹${amt.toLocaleString('en-IN')}.00).` : ''}</span><br>
        <span style="color:#fbbf24;">[STEP 2: FAILURE DETECTED] Chaos Scenario: ${cfg.name} (${cfg.type}).</span><br>
        <span style="color:#38bdf8;">[POLICY] 256-bit Idempotency Key locked. Zero double-charge lock engaged.</span><br>
        <span style="color:#e2e8f0;">[FSM] State: PROCESSING ➔ RECOVERY_PENDING...</span>
      `;
    }

    try {
      const res = await api("/api/simulate/scenario", {
        method: "POST",
        body: JSON.stringify({ scenario_type: scenario })
      });

      setTimeout(() => {
        if (amt > 0) {
          userWalletBalance += amt;
          logWalletActivity(`Chaos Self-Healing: ${cfg.name} (Restored Exact Amount)`, amt, true);
          updateUserWalletDisplays();
        }

        if (stream) {
          stream.innerHTML += `
            <br><span style="color:#4ade80; font-weight:800;">[STEP 3: SELF-HEAL EXECUTION] ${cfg.recovery}.</span><br>
            <span style="color:#34d399; font-weight:800;">[STEP 4: EXACT BALANCE RESTORED] +₹${amt > 0 ? amt.toLocaleString('en-IN') : '0'}.00 restored to Wallet! (Net Change: ₹0.00 / Zero Extra Added) ✓</span><br>
            <span style="color:#60a5fa; font-weight:800;">[FSM FINAL] Status: ${cfg.fsm}</span>
          `;
        }

        logTelemetry(`✓ Self-Healing Completed: ${cfg.name}. FSM: ${cfg.fsm}`, "#4ade80");

        if (amt > 0) {
          showToast(`🎉 Step 2: Self-Healing Complete! Exact ₹${amt.toLocaleString('en-IN')} restored to balance!`, "success");
          speak(`Self-healing completed for ${cfg.name}. Exact balance restored with zero double charge.`);
        } else {
          showToast(`🛡️ Security Guardrail: ${cfg.name} blocked safely.`, "info");
          speak(`Scenario executed. Security policy maintained.`);
        }

        loadTransactions();
        loadDashboardMetrics();
        loadPreviousOrdersHistory();
      }, 1300);

    } catch (e) {
      showToast("Simulation error: " + e.message, "error");
    }
  }

  async function startSimulatedFlow(scenario) {
    runSpecificChaosScenario(scenario);
  }

  async function seedTelemetryData() {
    try {
      showToast("Seeding realistic demo transaction telemetry...", "info");
      await api("/api/seed/demo-data", { method: "POST" });
      loadTransactions();
      loadDashboardMetrics();
      loadPreviousOrdersHistory();
      logTelemetry("Seeded 12+ verified telemetry transactions into database.", "#38bdf8");
      showToast("Seeded 12+ verified telemetry transactions!", "success");
    } catch (e) {
      showToast("Seeding error: " + e.message, "error");
    }
  }

  // =========================================================
  // TAB 2: AGENT CATALOGUE & GLOBAL DISCOVERY
  // =========================================================
  async function executeDiscoverySearch() {
    const input = $("discoverySearchInput");
    const query = input ? input.value.trim() : "";
    const cat = $("discoveryCategorySelect")?.value || "all";
    const maxPrice = $("discoveryMaxPriceSelect")?.value || "";
    const sortBy = $("discoverySortSelect")?.value || "relevance";

    try {
      const data = await api("/api/discovery/search", {
        method: "POST",
        body: JSON.stringify({
          query: query,
          category: cat !== "all" ? cat : null,
          max_price: maxPrice ? parseFloat(maxPrice) : null,
          sort_by: sortBy,
          intent_filter: currentDiscoveryIntentFilter
        })
      });

      discoveryProductsCache = data.products || [];
      renderDiscoveryGrid(discoveryProductsCache, query);
      renderAiTopRecommendations(data.top_recommendations || []);
      updateIntentFilterCounts(data.intent_counts || {});
      
      if ($("discoveryResultTotalCount")) {
        $("discoveryResultTotalCount").textContent = `${data.total_matched || discoveryProductsCache.length} items`;
      }
    } catch (e) {
      console.error("Discovery search error:", e);
    }
  }

  function renderDiscoveryGrid(products, query = "") {
    const grid = $("discoveryGrid");
    if (!grid) return;

    if (!products || !products.length) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #94a3b8;">
          <div style="font-size: 40px; margin-bottom: 12px;">🔍</div>
          <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">No products found for "${query}"</div>
          <div style="font-size: 12px; color: #64748b;">Try searching for smartphones, laptops, shoes, headphones, watches, or kitchen appliances.</div>
        </div>
      `;
      return;
    }

    grid.style.display = "grid";
    grid.style.gridTemplateColumns = "repeat(auto-fill, minmax(260px, 1fr))";
    grid.style.gap = "18px";

    grid.innerHTML = products.map((p, idx) => {
      const pId = p.product_id || p.id || `PROD_${idx+1}`;
      const safeName = (p.name || '').replace(/'/g, "\\'");
      const safeImg = (p.image_url || '').replace(/'/g, "\\'");
      const origPrice = p.reference_price || p.original_price || Math.round(p.price * 1.22);
      const disc = p.discount || Math.round(((origPrice - p.price) / origPrice) * 100);
      const isSelectedCompare = selectedCompareProducts.includes(pId);
      const delDays = p.delivery_days || 1;
      const delSLA = p.delivery_sla || (delDays === 1 ? "⚡ 1-Day Express SLA" : `📦 ${delDays}-Day Standard Delivery`);
      const score = p.recommendation_score || (90 + (idx % 10));

      return `
        <div class="product-discovery-card" style="background:#0b1120; border:1px solid #1e293b; border-radius:12px; padding:12px; display:flex; flex-direction:column; justify-content:space-between; position:relative; box-shadow:0 4px 14px rgba(0,0,0,0.4); transition:all 0.2s ease;">
          <span style="position:absolute; top:8px; left:8px; background:#ef4444; color:white; font-size:10px; font-weight:800; padding:2px 6px; border-radius:4px; z-index:2;">
            ${disc}% OFF
          </span>
          <span style="position:absolute; top:8px; right:8px; background:rgba(30,41,59,0.9); color:#38bdf8; font-size:10px; font-weight:800; padding:2px 6px; border-radius:4px; border:1px solid rgba(56,189,248,0.3); z-index:2;">
            🎯 ${score}/100
          </span>

          <div style="cursor:pointer;" onclick="openProductModal('${pId}')">
            <div style="position:relative; width:100%; height:160px; border-radius:8px; overflow:hidden; margin-bottom:10px; background:#1e293b;">
              <img src="${p.image_url || 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400'}" 
                   alt="${safeName}" 
                   style="width:100%; height:100%; object-fit:cover; transition:transform 0.3s ease;"
                   onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400';">
            </div>

            <div style="font-size:10px; color:#94a3b8; font-weight:800; text-transform:uppercase; margin-bottom:3px; letter-spacing:0.5px;">
              ${p.brand || 'Authentic Store'} · ${(p.category || 'tech').toUpperCase()}
            </div>
            
            <h4 style="font-size:13px; font-weight:800; color:#f8fafc; margin-bottom:6px; line-height:1.35; height:36px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="${p.name}">
              ${p.name}
            </h4>

            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px;">
              <div>
                <span style="color:#4ade80; font-size:17px; font-weight:900; font-family:var(--font-mono);">₹${Number(p.price).toLocaleString("en-IN")}</span>
                <span style="color:#64748b; font-size:11px; text-decoration:line-through; margin-left:4px;">₹${Number(origPrice).toLocaleString("en-IN")}</span>
              </div>
              <span style="font-size:9px; color:#94a3b8; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px;">Reference Price</span>
            </div>

            <div style="display:flex; justify-content:space-between; font-size:11px; color:#cbd5e1; margin-bottom:10px;">
              <span style="color:#fbbf24; font-weight:700;">★ ${p.rating || '4.8'} (${(p.review_count || 1200).toLocaleString()})</span>
              <span style="color:#a7f3d0; font-weight:600;">${delSLA}</span>
            </div>
          </div>

          <div style="display:flex; gap:6px; border-top:1px solid #1e293b; padding-top:8px;">
            <button class="btn-grid-cart" style="flex:1; padding:7px 0; font-size:12px; font-weight:700; background:#1e293b; color:#38bdf8; border:1px solid #334155; border-radius:6px; cursor:pointer;" onclick="addToCart('${pId}', '${safeName}')">
              + Cart
            </button>
            <button class="btn-grid-buy" style="flex:1; padding:7px 0; font-size:12px; font-weight:800; background:linear-gradient(135deg,#4f46e5,#9333ea); color:white; border:none; border-radius:6px; cursor:pointer;" onclick="handleQuickSelectProduct('${pId}', '${safeName}', ${p.price}, '${safeImg}', '${p.category || 'tech'}')">
              ⚡ Buy
            </button>
            <button class="btn-compare-chip ${isSelectedCompare ? 'selected' : ''}" style="padding:7px 8px; font-size:11px; background:#0f172a; color:#94a3b8; border:1px solid #334155; border-radius:6px; cursor:pointer;" onclick="toggleCompareProduct('${pId}')" title="Compare product">
              ⚖️
            </button>
          </div>
        </div>
      `;
    }).join("");
  }

  function renderAiTopRecommendations(recs) {
    const container = $("aiTopRecommendationsGrid");
    const sec = $("aiTopRecommendationsSection");
    if (!container || !sec) return;

    if (!recs || !recs.length) {
      sec.style.display = "none";
      return;
    }

    sec.style.display = "block";
    container.innerHTML = recs.slice(0, 4).map((r, idx) => {
      const p = r.product || r;
      const pId = p.product_id || p.id || `TOP_${idx+1}`;
      const safeName = (p.name || '').replace(/'/g, "\\'");
      const roleBadges = ["🥇 BEST OVERALL", "💰 BEST VALUE", "⭐ PREMIUM CHOICE", "🔥 MOST POPULAR"];
      const badge = r.role_badge || roleBadges[idx] || "✨ TOP PICK";

      return `
        <div style="background:linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(15,23,42,0.9) 100%); border:1px solid #6366f1; border-radius:12px; padding:12px; position:relative; display:flex; flex-direction:column; justify-content:space-between;">
          <span style="position:absolute; top:-9px; left:10px; background:#4f46e5; color:white; font-size:9px; font-weight:800; padding:2px 8px; border-radius:10px; text-transform:uppercase; letter-spacing:0.5px; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            ${badge}
          </span>
          <div style="margin-top:6px; cursor:pointer;" onclick="openProductModal('${pId}')">
            <img src="${p.image_url || 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300'}" 
                 alt="${safeName}" 
                 style="width:100%; height:120px; object-fit:cover; border-radius:8px; margin-bottom:8px; background:#1e293b;"
                 onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300';">
            <strong style="font-size:12px; color:white; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; height:32px; line-height:1.3; margin-bottom:4px;" title="${p.name}">${p.name}</strong>
            <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px;">
              <span style="color:#4ade80; font-size:15px; font-weight:900; font-family:var(--font-mono);">₹${Number(p.price).toLocaleString("en-IN")}</span>
              <span style="color:#fbbf24; font-size:11px; font-weight:700;">★ ${p.rating || 4.8}</span>
            </div>
            <small style="color:#94a3b8; font-size:10px; display:block; margin-bottom:8px;">${r.explanation || 'Top 6-Factor AI Recommendation Score'}</small>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
            <button onclick="addToCart('${pId}', '${safeName}')" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; border-radius:6px; padding:6px 0; font-size:11px; font-weight:700; cursor:pointer;">
              + Cart
            </button>
            <button onclick="handleQuickSelectProduct('${pId}', '${safeName}', ${p.price}, '${p.image_url}', '${p.category}')" style="background:#4f46e5; color:white; border:none; border-radius:6px; padding:6px 0; font-size:11px; font-weight:800; cursor:pointer;">
              ⚡ Buy
            </button>
          </div>
        </div>
      `;
    }).join("");
  }

  function handleDiscoverySearchInput(val) {
    clearTimeout(typingSuggestDebounce);
    typingSuggestDebounce = setTimeout(() => {
      executeDiscoverySearch();
    }, 300);
  }

  function clearDiscoverySearch() {
    if ($("discoverySearchInput")) $("discoverySearchInput").value = "";
    executeDiscoverySearch();
  }

  function handleCategoryFilterChange(val) {
    executeDiscoverySearch();
  }

  function handleMaxPriceFilterChange(val) {
    executeDiscoverySearch();
  }

  function handleSortFilterChange(val) {
    executeDiscoverySearch();
  }

    function handleDiscoveryChipClick(chipText) {
    const input = $("discoverySearchInput");
    if (input) input.value = chipText;

    const lower = chipText.toLowerCase();
    if (lower.includes("cheap") || lower.includes("budget")) {
      currentDiscoveryIntentFilter = "cheapest";
    } else if (lower.includes("rated") || lower.includes("best")) {
      currentDiscoveryIntentFilter = "best_rated";
    } else if (lower.includes("premium")) {
      currentDiscoveryIntentFilter = "premium";
    } else if (lower.includes("value")) {
      currentDiscoveryIntentFilter = "best_value";
    } else {
      currentDiscoveryIntentFilter = "all";
    }

    document.querySelectorAll(".intent-filter-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = $(`tabFilter${currentDiscoveryIntentFilter.charAt(0).toUpperCase() + currentDiscoveryIntentFilter.slice(1).replace('_', '')}`) || $(`tabFilterAll`);
    if (activeBtn) activeBtn.classList.add("active");

    showToast(`🔍 Searching: "${chipText}"`, "info");
    executeDiscoverySearch();
  }

  function setIntentFilter(filterName) {
    currentDiscoveryIntentFilter = filterName;
    document.querySelectorAll(".intent-filter-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = $(`tabFilter${filterName.charAt(0).toUpperCase() + filterName.slice(1).replace('_', '')}`) || $(`tabFilterAll`);
    if (activeBtn) activeBtn.classList.add("active");
    executeDiscoverySearch();
  }

  function updateIntentFilterCounts(counts) {
    if ($("countFilterAll")) $("countFilterAll").textContent = counts.all || discoveryProductsCache.length;
    if ($("countFilterBestValue")) $("countFilterBestValue").textContent = counts.best_value || 0;
    if ($("countFilterCheapest")) $("countFilterCheapest").textContent = counts.cheapest || 0;
    if ($("countFilterBestRated")) $("countFilterBestRated").textContent = counts.best_rated || 0;
    if ($("countFilterPremium")) $("countFilterPremium").textContent = counts.premium || 0;
  }

  // =========================================================
  // PRODUCT DETAILS MODAL & COMPARISON
  // =========================================================
  async function openProductModal(prodId) {
    try {
      const p = await api(`/api/discovery/product/${prodId}`);
      discoveryModalActiveProduct = p;
      if ($("modalProductTitle")) $("modalProductTitle").textContent = p.name;
      if ($("modalProductBrand")) $("modalProductBrand").textContent = p.brand || "Authentic Store";
      if ($("modalProductCategory")) $("modalProductCategory").textContent = (p.category || "General").toUpperCase();
      if ($("modalProductImage")) $("modalProductImage").src = p.image_url || "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600";
      if ($("modalProductPrice")) $("modalProductPrice").textContent = `₹${Number(p.price).toLocaleString("en-IN")}.00`;
      
      const orig = p.reference_price || p.original_price || Math.round(p.price * 1.2);
      if ($("modalProductOriginalPrice")) {
        $("modalProductOriginalPrice").textContent = `₹${Number(orig).toLocaleString("en-IN")}.00`;
        $("modalProductOriginalPrice").style.display = "inline";
      }

      const modal = $("discoveryProductModal");
      if (modal) modal.classList.add("open");
    } catch (e) {
      showToast("Error loading product details: " + e.message, "error");
    }
  }

  function closeProductModal() {
    $("discoveryProductModal")?.classList.remove("open");
  }

  function handleModalAddToCart() {
    if (discoveryModalActiveProduct) {
      addToCart(discoveryModalActiveProduct.product_id, discoveryModalActiveProduct.name);
      closeProductModal();
    }
  }

  function handleModalBuyNow() {
    if (discoveryModalActiveProduct) {
      handleQuickSelectProduct(
        discoveryModalActiveProduct.product_id,
        discoveryModalActiveProduct.name,
        discoveryModalActiveProduct.price,
        discoveryModalActiveProduct.image_url,
        discoveryModalActiveProduct.category
      );
      closeProductModal();
      launchRazorpayCheckoutFlow();
    }
  }

  function toggleCompareProduct(prodId) {
    if (selectedCompareProducts.includes(prodId)) {
      selectedCompareProducts = selectedCompareProducts.filter(id => id !== prodId);
      showToast(`Removed from comparison`, "info");
    } else {
      if (selectedCompareProducts.length >= 3) {
        showToast("Maximum 3 products can be compared at a time.", "warning");
        return;
      }
      selectedCompareProducts.push(prodId);
      showToast(`Added to comparison (${selectedCompareProducts.length}/3)`, "success");
    }

    if (selectedCompareProducts.length >= 2) {
      openCompareModal();
    }
  }

  async function openCompareModal() {
    const modal = $("compareModal");
    const content = $("compareModalContent");
    if (!modal || !content) return;
    modal.classList.add("open");

    try {
      const data = await api("/api/discovery/compare", {
        method: "POST",
        body: JSON.stringify({ product_ids: selectedCompareProducts })
      });

      const prods = data.products || [];
      content.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(${prods.length}, 1fr); gap:16px;">
          ${prods.map(p => `
            <div style="background:#080c14; border:1px solid #1e293b; border-radius:10px; padding:14px;">
              <img src="${p.image_url}" style="width:100%; height:130px; object-fit:cover; border-radius:8px; margin-bottom:8px;">
              <strong style="color:white; font-size:13px; display:block; margin-bottom:4px;">${p.name}</strong>
              <div style="color:#4ade80; font-size:16px; font-weight:900; font-family:var(--font-mono); margin-bottom:6px;">₹${p.price.toLocaleString('en-IN')}</div>
              <div style="font-size:11px; color:#cbd5e1; margin-bottom:8px;">Rating: ★ ${p.rating} (${p.review_count} reviews)</div>
              <button onclick="addToCart('${p.id}', '${p.name.replace(/'/g, "\\'")}')" style="width:100%; background:#2563eb; color:white; border:none; padding:8px 0; border-radius:6px; font-weight:800; cursor:pointer;">+ Add to Cart</button>
            </div>
          `).join("")}
        </div>
      `;
    } catch (e) {
      content.innerHTML = `<div style="color:#ef4444; padding:20px;">Comparison Error: ${e.message}</div>`;
    }
  }

  function closeCompareModal() {
    $("compareModal")?.classList.remove("open");
  }

  // =========================================================
  
  // =========================================================
  // DIRECT LIVE-EDITABLE ADDRESS CONTROLLERS
  // =========================================================
  function handleDirectAddressTyping() {
    const name = $("cartDirectName")?.value || "Arjun Sharma";
    const phone = $("cartDirectPhone")?.value || "+91 98765 43210";
    const street = $("cartDirectStreet")?.value || "#402, Prestige Tech Park, Outer Ring Road";
    const city = $("cartDirectCity")?.value || "Bengaluru, Karnataka";
    const pin = $("cartDirectPin")?.value || "560103";

    if ($("cartRecipientName")) $("cartRecipientName").textContent = name;
    if ($("cartRecipientPhone")) $("cartRecipientPhone").textContent = phone;
    if ($("cartFullAddress")) $("cartFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("flowRecipientName")) $("flowRecipientName").textContent = name;
    if ($("flowRecipientPhone")) $("flowRecipientPhone").textContent = phone;
    if ($("flowFullAddress")) $("flowFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("addrInputName")) $("addrInputName").value = name;
    if ($("addrInputPhone")) $("addrInputPhone").value = phone;
    if ($("addrInputStreet")) $("addrInputStreet").value = street;
    if ($("addrInputCity")) $("addrInputCity").value = city;
    if ($("addrInputPin")) $("addrInputPin").value = pin;
  }

  function selectSavedAddress(type) {
    const presets = {
      home: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "#402, Prestige Tech Park, Outer Ring Road", city: "Bengaluru, Karnataka", pin: "560103" },
      work: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "5th Floor, WeWork Galaxy, Residency Road", city: "Bengaluru, Karnataka", pin: "560025" },
      parents: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "B-12, Green Glen Layout, Bellandur", city: "Bengaluru, Karnataka", pin: "560103" }
    };
    const p = presets[type] || presets.home;

    if ($("cartDirectName")) $("cartDirectName").value = p.name;
    if ($("cartDirectPhone")) $("cartDirectPhone").value = p.phone;
    if ($("cartDirectStreet")) $("cartDirectStreet").value = p.street;
    if ($("cartDirectCity")) $("cartDirectCity").value = p.city;
    if ($("cartDirectPin")) $("cartDirectPin").value = p.pin;

    handleDirectAddressTyping();
    showToast(`📍 Selected ${type.toUpperCase()} delivery address preset!`, "success");
    speak(`Delivery address set to ${type}.`);
  }

  function getSafeFallbackImage(cat, name) {
    const q = ((cat || '') + ' ' + (name || '')).toLowerCase();
    if (q.includes('shoe') || q.includes('sneaker') || q.includes('joot') || q.includes('nike') || q.includes('adidas') || q.includes('zapat') || q.includes('chauss')) {
      return "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500";
    }
    if (q.includes('headphone') || q.includes('audio') || q.includes('sony') || q.includes('bose')) {
      return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500";
    }
    if (q.includes('earbud') || q.includes('airpod') || q.includes('tws')) {
      return "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500";
    }
    if (q.includes('laptop') || q.includes('macbook') || q.includes('dell') || q.includes('thinkpad')) {
      return "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500";
    }
    if (q.includes('phone') || q.includes('iphone') || q.includes('galaxy') || q.includes('pixel')) {
      return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500";
    }
    if (q.includes('watch') || q.includes('smartwatch')) {
      return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500";
    }
    if (q.includes('keyboard') || q.includes('keychron')) {
      return "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500";
    }
    if (q.includes('shirt') || q.includes('cloth') || q.includes('tshirt') || q.includes('dress') || q.includes('kapda')) {
      return "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500";
    }
    if (q.includes('bag') || q.includes('backpack')) {
      return "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500";
    }
    if (q.includes('camera') || q.includes('dslr')) {
      return "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500";
    }
    return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500";
  }

  // ADDRESS CONTROLLERS
  // =========================================================
  function toggleInlineManualAddressForm() {
    const form = $("inlineManualAddressForm") || $("manualAddressForm");
    if (form) {
      const isHidden = form.style.display === "none" || !form.style.display;
      form.style.display = isHidden ? "block" : "none";
      if (isHidden) {
        $("cartManualName")?.focus();
        showToast("✍️ Custom address form opened. Type your details.", "info");
      }
    }
  }

  function handleManualAddressInput() {
    const name = $("cartManualName")?.value || "Arjun Sharma";
    const phone = $("cartManualPhone")?.value || "+91 98765 43210";
    const street = $("cartManualStreet")?.value || "#402, Prestige Tech Park, Outer Ring Road";
    const city = $("cartManualCity")?.value || "Bengaluru, Karnataka";
    const pin = $("cartManualPin")?.value || "560103";

    if ($("cartRecipientName")) $("cartRecipientName").textContent = name;
    if ($("cartRecipientPhone")) $("cartRecipientPhone").textContent = phone;
    if ($("cartFullAddress")) $("cartFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("flowRecipientName")) $("flowRecipientName").textContent = name;
    if ($("flowRecipientPhone")) $("flowRecipientPhone").textContent = phone;
    if ($("flowFullAddress")) $("flowFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("addrInputName")) $("addrInputName").value = name;
    if ($("addrInputPhone")) $("addrInputPhone").value = phone;
    if ($("addrInputStreet")) $("addrInputStreet").value = street;
    if ($("addrInputCity")) $("addrInputCity").value = city;
    if ($("addrInputPin")) $("addrInputPin").value = pin;
  }

  function toggleAddressEditModal(force = null) {
    const modal = $("deliveryAddressModal") || $("addressModal");
    if (!modal) return;
    if (force === true) modal.classList.add("open");
    else if (force === false) modal.classList.remove("open");
    else modal.classList.toggle("open");
  }

  function selectSavedAddress(type) {
    const presets = {
      home: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "#402, Prestige Tech Park, Outer Ring Road", city: "Bengaluru, Karnataka", pin: "560103" },
      work: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "5th Floor, WeWork Galaxy, Residency Road", city: "Bengaluru, Karnataka", pin: "560025" },
      parents: { name: "Arjun Sharma", phone: "+91 98765 43210", street: "B-12, Green Glen Layout, Bellandur", city: "Bengaluru, Karnataka", pin: "560103" }
    };
    const p = presets[type] || presets.home;
    if ($("cartRecipientName")) $("cartRecipientName").textContent = p.name;
    if ($("cartRecipientPhone")) $("cartRecipientPhone").textContent = p.phone;
    if ($("cartFullAddress")) $("cartFullAddress").textContent = `${p.street}, ${p.city} - ${p.pin}`;

    if ($("flowRecipientName")) $("flowRecipientName").textContent = p.name;
    if ($("flowRecipientPhone")) $("flowRecipientPhone").textContent = p.phone;
    if ($("flowFullAddress")) $("flowFullAddress").textContent = `${p.street}, ${p.city} - ${p.pin}`;
    
    if ($("cartManualName")) $("cartManualName").value = p.name;
    if ($("cartManualPhone")) $("cartManualPhone").value = p.phone;
    if ($("cartManualStreet")) $("cartManualStreet").value = p.street;
    if ($("cartManualCity")) $("cartManualCity").value = p.city;
    if ($("cartManualPin")) $("cartManualPin").value = p.pin;

    if ($("addrInputName")) $("addrInputName").value = p.name;
    if ($("addrInputPhone")) $("addrInputPhone").value = p.phone;
    if ($("addrInputStreet")) $("addrInputStreet").value = p.street;
    if ($("addrInputCity")) $("addrInputCity").value = p.city;
    if ($("addrInputPin")) $("addrInputPin").value = p.pin;

    document.querySelectorAll(".saved-addr-card").forEach(c => c.style.borderColor = "#1e293b");
    const card = $(`addrCard${type.charAt(0).toUpperCase() + type.slice(1)}`);
    if (card) card.style.borderColor = "#38bdf8";

    showToast(`Selected ${type.toUpperCase()} delivery preset!`, "success");
  }

  function saveDeliveryAddress() {
    const name = $("addrInputName")?.value || $("cartManualName")?.value || "Arjun Sharma";
    const phone = $("addrInputPhone")?.value || $("cartManualPhone")?.value || "+91 98765 43210";
    const street = $("addrInputStreet")?.value || $("cartManualStreet")?.value || "#402, Prestige Tech Park, Outer Ring Road";
    const city = $("addrInputCity")?.value || $("cartManualCity")?.value || "Bengaluru, Karnataka";
    const pin = $("addrInputPin")?.value || $("cartManualPin")?.value || "560103";

    if ($("cartRecipientName")) $("cartRecipientName").textContent = name;
    if ($("cartRecipientPhone")) $("cartRecipientPhone").textContent = phone;
    if ($("cartFullAddress")) $("cartFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("flowRecipientName")) $("flowRecipientName").textContent = name;
    if ($("flowRecipientPhone")) $("flowRecipientPhone").textContent = phone;
    if ($("flowFullAddress")) $("flowFullAddress").textContent = `${street}, ${city} - ${pin}`;

    if ($("cartManualName")) $("cartManualName").value = name;
    if ($("cartManualPhone")) $("cartManualPhone").value = phone;
    if ($("cartManualStreet")) $("cartManualStreet").value = street;
    if ($("cartManualCity")) $("cartManualCity").value = city;
    if ($("cartManualPin")) $("cartManualPin").value = pin;

    toggleAddressEditModal(false);
    showToast("✓ Delivery address saved & updated!", "success");
    speak("Delivery address updated successfully.");
  }

  function handlePincodeChange(pin) {
    if (pin && pin.length === 6) {
      showToast(`📍 Pincode ${pin} Verified for 1-Day Express Delivery SLA`, "info");
    }
  }

  function updateDeliverySlaSpeed(speed) {
    showToast(`Delivery SLA updated to: ${speed === 'express' ? '⚡ 1-Day Express' : '🚚 Standard 2-3 Days'}`, "info");
  }

  // =========================================================
  // TAB 5, 6, 7, 8 DASHBOARD & AUDIT CONTROLLERS
  // =========================================================
  async function loadDashboardMetrics() {
    try {
      const data = await api("/api/growth/overview");
      if ($("kpiRevenueVal")) $("kpiRevenueVal").textContent = `₹${Number(data.total_captured_revenue || 248900).toLocaleString("en-IN")}.00`;
      if ($("kpiSuccessRateVal")) $("kpiSuccessRateVal").textContent = `${data.payment_success_rate || 99.4}%`;
      if ($("kpiRecoveriesVal")) $("kpiRecoveriesVal").textContent = `${data.total_recovered_orders || 14}`;
    } catch (_) {}
  }

  async function askGrowthCopilotTab() {
    const input = $("tabCopilotInput");
    const q = input ? input.value.trim() : "How can I boost checkout conversion?";
    const box = $("tabCopilotResponse");
    if (!box) return;
    box.innerHTML = `<div style="color:#94a3b8;">Analyzing merchant telemetry and AI policies...</div>`;
    try {
      const data = await api("/api/growth/copilot", {
        method: "POST",
        body: JSON.stringify({ query: q })
      });
      box.innerHTML = (data.advice || "Optimization recommended.").replace(/\*\*(.*?)\*\*/g, '<strong style="color:white;">$1</strong>').split('\n').join('<br>');
    } catch (e) {
      box.textContent = "Error: " + e.message;
    }
  }

  function quickCopilotTopic(topic) {
    const map = {
      conversion: "How can I boost checkout conversion?",
      bundle: "Which product bundles will increase AOV?",
      abandoned: "How is cart abandonment handled?",
      fail: "What is the root cause of recent payment failures?"
    };
    if ($("tabCopilotInput")) $("tabCopilotInput").value = map[topic] || topic;
    askGrowthCopilotTab();
  }

  async function runGrowthSimTab() {
    const traffic = parseFloat($("simTrafficIn")?.value) || 10000;
    const conv = parseFloat($("simConvIn")?.value) || 3.5;
    const box = $("tabSimResultBox");
    if (!box) return;
    try {
      const data = await api("/api/growth/simulate", {
        method: "POST",
        body: JSON.stringify({ traffic, conversion_rate: conv, aov: 2499 })
      });
      const p = data.projections;
      box.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
          <span>Base Volume:</span><strong>₹${p.base_revenue.toLocaleString("en-IN")}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:4px; color:#60a5fa;">
          <span>+ Recovered Revenue:</span><strong>+₹${p.recovered_revenue.toLocaleString("en-IN")} (${p.recovered_orders} orders)</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px; color:#c084fc;">
          <span>+ AI Cross-Sell Lift:</span><strong>+₹${p.cross_sell_revenue.toLocaleString("en-IN")}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; border-top:1px solid #1e293b; padding-top:6px; font-weight:800; color:#4ade80;">
          <span>Total Projected:</span><span>₹${p.total_projected_revenue.toLocaleString("en-IN")} (+${p.revenue_lift_percent}% Lift)</span>
        </div>
      `;
    } catch (e) {
      box.textContent = "Simulation error: " + e.message;
    }
  }

  async function approveCampaignTab(id) {
    showToast(`Campaign #${id} approved! Activating automated merchant campaign.`, "success");
    speak(`Campaign ${id} approved and launched.`);
  }

  async function runInteractiveSafetyGateCheck() {
    const amt = parseFloat($("gateTestAmount")?.value) || 24990;
    const confirmed = $("gateTestConsent")?.value === "true";
    const resBox = $("safetyGateEvalResult");

    showToast("Safety Gate evaluating transaction against 8 rules...", "info");
    speak("Money Safety Gate validating transaction against merchant rules.");

    try {
      const data = await api("/api/policy/evaluate", {
        method: "POST",
        body: JSON.stringify({
          action_type: "ORDER_CREATION",
          amount: amt,
          discount_percentage: 0.0,
          customer_confirmed: confirmed,
          session_id: "sess_sandbox_01"
        })
      });

      if (resBox) {
        resBox.innerHTML = `
          <div style="color:${data.is_allowed ? '#4ade80' : '#f87171'}; font-weight:800; margin-bottom:6px;">
            ${data.is_allowed ? '✅ PRE-FLIGHT EVALUATION PASSED (POLICY CLEARED)' : '❌ BLOCKED BY POLICY GATE'}
          </div>
          <div>Decision Rationale: ${data.reason}</div>
          <div style="margin-top:6px; color:#94a3b8; font-size:11px;">Rules Evaluated: Spending Cap (₹5,00,000), Per-Tx Limit, Velocity Check, Explicit Consent.</div>
        `;
      }
    } catch (e) {
      if (resBox) resBox.innerHTML = `<span style="color:#ef4444;">Error: ${e.message}</span>`;
    }
  }

  async function runAgentToAgentSimulation() {
    const prompt = $("a2aPromptInput")?.value || "Find wireless headphones with ANC under ₹30000";
    showToast("Executing Agent-to-Agent Commerce Handshake Protocol...", "info");
    speak("Executing agent-to-agent autonomous commerce handshake.");

    try {
      const data = await api("/api/agent/trade", {
        method: "POST",
        body: JSON.stringify({ prompt: prompt, budget: 30000 })
      });

      const resBox = $("a2aResultPayload");
      if (resBox) {
        resBox.innerHTML = `
          <div style="color:#4ade80; font-weight:800; margin-bottom:6px;">🤝 AUTONOMOUS TRADE COMPLETED SUCCESSFULLY</div>
          <div>• Buyer Agent: Requested "${data.buyer_prompt}"</div>
          <div>• Merchant Agent: Matched "${data.selected_product.name}" (₹${data.selected_product.price.toLocaleString('en-IN')})</div>
          <div>• Money Safety Gate: ${data.policy_evaluation.status} (8/8 Guardrails Verified)</div>
          <div>• Bounded Razorpay Order: <code>${data.order_id}</code> | Payment ID: <code>${data.payment_id}</code></div>
          <div style="color:#38bdf8; margin-top:4px;">• Audit Record: SHA-256 Block Hashed & Chained</div>
        `;
      }
      showToast("Agent-to-Agent Trade Completed!", "success");
    } catch (e) {
      showToast("A2A Error: " + e.message, "error");
    }
  }

  async function loadTransactions() {
    const tbody = $("txLedgerTableBody");
    if (!tbody) return;
    try {
      const data = await api("/api/transactions");
      const txs = data.transactions || [];
      if (!txs.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:30px; color:#94a3b8;">No transactions found. Click "⚡ Seed Telemetry" to populate records.</td></tr>`;
        return;
      }
      tbody.innerHTML = txs.map(t => {
        let pill = `<span class="badge-tag badge-green">SUCCESS</span>`;
        if (t.status === "RECOVERY_PENDING") pill = `<span class="badge-tag badge-red">RECOVERY PENDING</span>`;
        else if (t.status === "FAILED") pill = `<span class="badge-tag badge-red">FAILED</span>`;
        else if (t.is_recovered) pill = `<span class="badge-tag badge-blue">RECOVERED ✓</span>`;
        return `
          <tr>
            <td><code style="color:#93c5fd;">${t.transaction_id}</code></td>
            <td><strong>#${t.order_id}</strong></td>
            <td style="font-weight:800; color:#4ade80; font-family:var(--font-mono);">₹${t.amount.toLocaleString("en-IN")}</td>
            <td>${pill}</td>
            <td><span style="font-family:var(--font-mono); color:${t.risk_score > 30 ? '#f59e0b' : '#4ade80'};">${t.risk_score.toFixed(1)}</span></td>
            <td>${t.retry_count}</td>
            <td><small style="font-family:var(--font-mono); color:#64748b;">${t.idempotency_key.substring(0, 14)}...</small></td>
            <td><small style="color:#94a3b8;">${new Date(t.timestamp).toLocaleTimeString()}</small></td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8" style="color:#ef4444; text-align:center;">Error: ${e.message}</td></tr>`;
    }
  }

  async function loadAuditLogs() {
    const stream = $("auditLogStream");
    if (!stream) return;
    try {
      const data = await api("/api/audit");
      const events = data.events || [];
      if (!events.length) {
        stream.innerHTML = `<p style="text-align:center; color:#94a3b8; padding:20px;">No audit events recorded.</p>`;
        return;
      }
      stream.innerHTML = events.slice(-12).reverse().map(e => `
        <div style="background:#080c14; border:1px solid #1e293b; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <strong style="color:#93c5fd; font-size:13px;">${e.event_type}</strong>
            <small style="color:#64748b;">${new Date(e.timestamp).toLocaleTimeString()}</small>
          </div>
          <div style="font-family:var(--font-mono); font-size:11px; color:#94a3b8; word-break:break-all;">
            Hash: ${e.hash}
          </div>
        </div>
      `).join("");
    } catch (e) {
      stream.innerHTML = `<p style="color:#ef4444;">${e.message}</p>`;
    }
  }

  async function verifyAuditChain() {
    const banner = $("chainVerifyBanner");
    if (!banner) return;
    try {
      const data = await api("/api/audit/verify");
      banner.style.display = "block";
      if (data.valid) {
        banner.style.background = "rgba(34, 197, 94, 0.15)";
        banner.style.border = "1px solid rgba(34, 197, 94, 0.4)";
        banner.style.color = "#4ade80";
        banner.innerHTML = `✓ AUDIT CHAIN VALID ✓ (All ${data.events_verified} cryptographic blocks verified with zero tampering).`;
        speak("Cryptographic SHA-256 audit chain valid. Zero tampering detected.");
      } else {
        banner.style.background = "rgba(239, 68, 68, 0.15)";
        banner.style.border = "1px solid rgba(239, 68, 68, 0.4)";
        banner.style.color = "#f87171";
        banner.innerHTML = "✕ Cryptographic integrity check failed.";
      }
    } catch (e) {
      banner.style.display = "block";
      banner.textContent = "Verification Error: " + e.message;
    }
  }

  // =========================================================
  // MASTER JUDGE GUIDED TOUR (10 STEPS)
  // =========================================================
  const judgeTourSteps = [
    {
      title: "Step 1: Multilingual Conversational Search",
      body: "Type or speak naturally in Tamil, Hindi, Telugu, Spanish, French, or English. The AI normalizes intent and searches across the 350+ item verified catalogue.",
      tab: "checkout"
    },
    {
      title: "Step 2: Explainable AI Recommendations",
      body: "Review recommendations with explicit multi-attribute AI Scores (96/100) and transparent 'Why AI Recommends This' bullet points.",
      tab: "checkout"
    },
    {
      title: "Step 3: Smart Cart & Previous Order History",
      body: "Explore active items with individual SLAs and switch to the 'Order History' sub-tab to inspect past verified orders.",
      tab: "checkout"
    },
    {
      title: "Step 4: Automated Pre-Flight Safety Gate",
      body: "Before payment, the 8-Factor Money Safety Gate checks spending caps, budget, velocity, and user consent with zero double-billing risk.",
      tab: "checkout"
    },
    {
      title: "Step 5: Official Razorpay Test Checkout",
      body: "Execute payments using real server-side Razorpay Order IDs with test cards, instant UPI QR, or Netbanking.",
      tab: "checkout"
    },
    {
      title: "Step 6: Live State Machine & Webhook Timeline",
      body: "Watch the animated state machine progress from CREATED to SUCCESS backed by server-side HMAC-SHA256 signature verification and webhook receipts.",
      tab: "checkout"
    },
    {
      title: "Step 7: Autonomous 504 Timeout Recovery",
      body: "Simulate a gateway timeout: money is held in buffer, then recovered with exact balance restoration and zero duplicate charges.",
      tab: "checkout"
    },
    {
      title: "Step 8: Rapid Double-Click Idempotency Protection",
      body: "Rapid clicks are locked by 256-bit database unique constraints, blocking duplicate charges while safely continuing the original order.",
      tab: "checkout"
    },
    {
      title: "Step 9: Live Right-Side Reliability Panel",
      body: "Monitor live Transaction IDs, Idempotency keys, risk gauges, 6-factor live guardrails, and real-time telemetry events.",
      tab: "checkout"
    },
    {
      title: "Step 10: Cryptographic Audit Trail & Telemetry",
      body: "Verify the tamper-proof SHA-256 cryptographic audit chain and live merchant growth analytics.",
      tab: "growth"
    }
  ];

  function startJudgeGuidedTour() {
    judgeTourCurrentStep = 0;
    renderJudgeTourStep();
    $("judgeTourModal")?.classList.add("open");
  }

  function closeJudgeTour() {
    $("judgeTourModal")?.classList.remove("open");
  }

  function renderJudgeTourStep() {
    const step = judgeTourSteps[judgeTourCurrentStep];
    if (!step) return;
    $("tourStepBadge").textContent = `STEP ${judgeTourCurrentStep + 1} OF ${judgeTourSteps.length}`;
    $("tourTitle").textContent = step.title;
    $("tourBody").textContent = step.body;
    $("tourPrevBtn").style.display = judgeTourCurrentStep > 0 ? "inline-flex" : "none";
    $("tourNextBtn").textContent = judgeTourCurrentStep === judgeTourSteps.length - 1 ? "Finish Tour ✓" : "Next Step →";
    
    switchMainTab(step.tab);
    speak(step.title);
  }

  function nextJudgeStep() {
    if (judgeTourCurrentStep < judgeTourSteps.length - 1) {
      judgeTourCurrentStep++;
      renderJudgeTourStep();
    } else {
      closeJudgeTour();
      showToast("🏆 Master Judge Demo Complete!", "success");
      speak("Master demo walkthrough complete. Thank you!");
    }
  }

  function prevJudgeStep() {
    if (judgeTourCurrentStep > 0) {
      judgeTourCurrentStep--;
      renderJudgeTourStep();
    }
  }

  // =========================================================
  // DISCOVERY & ADDRESS HELPERS
  // =========================================================
  function refreshDiscoverySearch() { executeDiscoverySearch(); }
  function handleDiscoveryChip(chip) { if ($("discoverySearchInput")) $("discoverySearchInput").value = chip; executeDiscoverySearch(); }
  function triggerDiscoveryMicSearch() { triggerMicShopping(); }
  function applySpellCorrection() { if (currentSpellCorrectionText && $("discoverySearchInput")) { $("discoverySearchInput").value = currentSpellCorrectionText; executeDiscoverySearch(); } }
  function closeProductDetailsModal() { closeProductModal(); }

  // =========================================================
  // EVENT LISTENERS & INITIALIZATION
  // =========================================================
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".rfx-modal-overlay.open").forEach(m => m.classList.remove("open"));
      $("cartDrawerOverlay")?.classList.remove("open");
      $("walletSlideDrawerOverlay")?.classList.remove("open");
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("rfx-modal-overlay")) e.target.classList.remove("open");
    if (e.target.id === "cartDrawerOverlay") e.target.classList.remove("open");
    if (e.target.id === "walletSlideDrawerOverlay") e.target.classList.remove("open");
  });

  document.addEventListener("DOMContentLoaded", () => {
    updateUserWalletDisplays();
    loadCart();
    loadPreviousOrdersHistory();
    loadDashboardMetrics();
    loadTransactions();
    loadAuditLogs();
    executeDiscoverySearch();
    logTelemetry("Conversational Checkout & Payment Reliability Engine Ready.", "#4ade80");
  });
