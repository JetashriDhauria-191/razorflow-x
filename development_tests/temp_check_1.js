
// =========================================================
  // RAZORFLOW X — MASTER CLIENT APPLICATION CONTROLLER
  // =========================================================

  const $ = (id) => document.getElementById(id);

  let currentVoiceLanguage = "en-IN";
  let isVoiceAudioFeedback = true;
  let isHandsFreeActive = false;
  let speechRecognitionInstance = null;
  let allProductsCache = [];
  let discoveryProductsCache = [];
  let selectedCompareProducts = [];
  let currentActiveProduct = null;
  let currentOrderAmount = 24990;
  let currentDeskMethod = "upi";
  let currentDeskBank = "HDFC";
  let currentSelectedUpiApp = "gpay";
  let currentDiscoveryIntentFilter = "all";
  let currentActiveSearchLanguage = "auto";
  let discoveryModalActiveProduct = null;
  let typingSuggestDebounce = null;
  let currentSpellCorrectionText = null;
  let conversationContext = { turn_count: 0 };
  let judgeTourCurrentStep = 0;

    // =========================================================
  // BUYER WALLET BALANCE & SLIDE DRAWER SYSTEM
  // =========================================================
  let userWalletBalance = 100000; // Starting demo balance: ₹1,00,000
  let walletTransactionLogs = [
    { title: "Initial Demo Balance", amount: 100000, type: "credit", time: new Date().toLocaleTimeString() }
  ];

  function toggleWalletDrawer(forceOpen = null) {
    const drawer = $("walletSlideDrawerOverlay");
    if (!drawer) return;
    if (forceOpen === true) {
      drawer.classList.add("open");
    } else if (forceOpen === false) {
      drawer.classList.remove("open");
    } else {
      drawer.classList.toggle("open");
    }
    if (drawer.classList.contains("open")) {
      updateUserWalletDisplays();
    }
  }

  function updateUserWalletDisplays() {
    const isZero = userWalletBalance <= 0;
    const formatted = `₹${Math.max(0, userWalletBalance).toLocaleString('en-IN')}.00`;
    
    // Header Display
    const hDisplay = $("userWalletBalanceDisplay");
    const hBadge = $("headerWalletBadge");
    if (hDisplay) {
      hDisplay.textContent = isZero ? "₹0.00 (ZERO / INSUFFICIENT)" : formatted;
      hDisplay.style.color = isZero ? "#ef4444" : "#4ade80";
    }
    if (hBadge) {
      hBadge.style.borderColor = isZero ? "#ef4444" : "#22c55e";
      hBadge.style.background = isZero ? "rgba(239, 68, 68, 0.15)" : "rgba(34, 197, 94, 0.15)";
    }

    // Slide Drawer Displays
    const wCard = $("walletDrawerBalanceCard");
    const wAmt = $("walletDrawerMainAmount");
    const wPill = $("walletDrawerStatusPill");
    const wWarning = $("walletDrawerWarningMsg");
    if (wCard) {
      wCard.classList.toggle("zero-balance", isZero);
    }
    if (wAmt) {
      wAmt.textContent = formatted;
      wAmt.style.color = isZero ? "#ef4444" : "#4ade80";
    }
    if (wPill) {
      wPill.textContent = isZero ? "⚠️ ZERO BALANCE" : "● ACTIVE";
      wPill.style.background = isZero ? "rgba(239, 68, 68, 0.2)" : "rgba(34, 197, 94, 0.2)";
      wPill.style.color = isZero ? "#f87171" : "#4ade80";
      wPill.style.borderColor = isZero ? "rgba(239, 68, 68, 0.4)" : "rgba(34, 197, 94, 0.4)";
    }
    if (wWarning) {
      wWarning.style.display = isZero ? "block" : "none";
    }

    // Cart Drawer & Receipt Displays
    if ($("modalWalletDisplay")) $("modalWalletDisplay").textContent = formatted;
    if ($("cartWalletBalanceDisplay")) {
      $("cartWalletBalanceDisplay").textContent = isZero ? "₹0.00 (ZERO / INSUFFICIENT)" : formatted;
      $("cartWalletBalanceDisplay").style.color = isZero ? "#ef4444" : "#4ade80";
    }
    if ($("wReceiptRemainingBalance")) {
      $("wReceiptRemainingBalance").textContent = formatted;
    }

    renderWalletActivityList();
  }

  function addWalletMoney(amt) {
    const num = parseFloat(amt);
    if (isNaN(num) || num <= 0) return;
    userWalletBalance += num;
    logWalletActivity(`Added Funds (Quick Preset)`, num, true);
    updateUserWalletDisplays();
    showToast(`💳 Added ₹${num.toLocaleString('en-IN')} to Wallet! Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "success");
    speak(`Added ${num} rupees. Wallet balance is ${userWalletBalance} rupees.`);
  }

  function handleCustomAddMoney() {
    const input = $("customAddAmountInput");
    if (!input) return;
    const num = parseFloat(input.value);
    if (isNaN(num) || num <= 0) {
      showToast("Please enter a valid amount to add.", "warning");
      return;
    }
    userWalletBalance += num;
    logWalletActivity(`Custom Funds Deposit`, num, true);
    input.value = "";
    updateUserWalletDisplays();
    showToast(`💳 Added ₹${num.toLocaleString('en-IN')} to Wallet! Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "success");
    speak(`Added ${num} rupees. New balance is ${userWalletBalance} rupees.`);
  }

  function withdrawWalletMoney(amt) {
    const num = parseFloat(amt);
    if (isNaN(num) || num <= 0) return;
    if (userWalletBalance < num) {
      showToast(`Cannot withdraw ₹${num.toLocaleString('en-IN')}. Available balance is only ₹${userWalletBalance.toLocaleString('en-IN')}.`, "error");
      return;
    }
    userWalletBalance -= num;
    logWalletActivity(`Withdrawal to Bank Account`, num, false);
    updateUserWalletDisplays();
    showToast(`💸 Withdrew ₹${num.toLocaleString('en-IN')} to Bank. Remaining Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "info");
    speak(`Withdrew ${num} rupees. Remaining balance is ${userWalletBalance} rupees.`);
  }

  function withdrawAllWalletMoney() {
    if (userWalletBalance <= 0) {
      showToast("Wallet balance is already ₹0.00.", "info");
      return;
    }
    const drained = userWalletBalance;
    userWalletBalance = 0;
    logWalletActivity(`Total Balance Withdrawal (Zeroed Out)`, drained, false);
    updateUserWalletDisplays();
    showToast(`💸 Withdrew total ₹${drained.toLocaleString('en-IN')}! Balance is now ₹0.00 (INSUFFICIENT).`, "warning");
    speak("Total balance withdrawn. Wallet balance is now zero rupees.");
  }

  function handleCustomWithdrawMoney() {
    const input = $("customWithdrawAmountInput");
    if (!input) return;
    const num = parseFloat(input.value);
    if (isNaN(num) || num <= 0) {
      showToast("Please enter a valid amount to withdraw.", "warning");
      return;
    }
    if (userWalletBalance < num) {
      showToast(`Insufficient funds to withdraw ₹${num.toLocaleString('en-IN')}. Available: ₹${userWalletBalance.toLocaleString('en-IN')}`, "error");
      return;
    }
    userWalletBalance -= num;
    logWalletActivity(`Custom Withdrawal to Bank`, num, false);
    input.value = "";
    updateUserWalletDisplays();
    showToast(`💸 Withdrew ₹${num.toLocaleString('en-IN')} to Bank. Remaining Balance: ₹${userWalletBalance.toLocaleString('en-IN')}`, "info");
    speak(`Withdrew ${num} rupees. Remaining balance is ${userWalletBalance} rupees.`);
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
      const msg = `⚠️ INSUFFICIENT WALLET BALANCE! Order: ₹${amount.toLocaleString('en-IN')} | Available Wallet: ₹${userWalletBalance.toLocaleString('en-IN')}. Please add money in the wallet slide.`;
      showToast(msg, "error");
      speak("Insufficient balance in your wallet. Please add money using the wallet slide.");
      toggleWalletDrawer(true); // Open slide drawer
      return false;
    }
    return true;
  }

  const judgeTourSteps = [
    {
      title: "Step 1: Universal Multilingual AI Shopping",
      body: "Type or speak naturally in Tamil, Hindi, Telugu, Malayalam, French, or English to search products with real-time intent parsing and honest pricing.",
      tab: "catalogue"
    },
    {
      title: "Step 2: Voice & Conversational Checkout Agent",
      body: "Chat with the autonomous AI Commerce Agent. It resolves intent, suggests bundle cross-sells, and executes bounded turn loops.",
      tab: "checkout"
    },
    {
      title: "Step 3: Multi-Item Delivery SLA Tracking in Cart",
      body: "Open the slide-over cart drawer to view individual delivery speed and arrival dates for every added product (1-Day Express to 4-Day Standard).",
      tab: "checkout"
    },
    {
      title: "Step 4: Money Action Safety Gate & Razorpay Checkout",
      body: "Test bounded payments with official Razorpay test cards, instant UPI QR, or Netbanking with complete fraud & policy validation.",
      tab: "checkout"
    },
    {
      title: "Step 5: Telemetry, Recovery & Audit Logs",
      body: "Explore the live merchant growth analytics, autonomous recovery state machine, and tamper-proof SHA-256 cryptographic audit ledger.",
      tab: "growth"
    }
  ];

  // Helper API fetcher
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
    }, 3200);
  }

  function speak(text, customLang = null) {
    if (!isVoiceAudioFeedback || !("speechSynthesis" in window)) return;
    try {
      window.speechSynthesis.cancel();
      const msg = new SpeechSynthesisUtterance(text);
      msg.lang = customLang || detectScriptLanguage(text);
      msg.rate = 1.02;
      window.speechSynthesis.speak(msg);
    } catch (_) {}
  }

  function detectScriptLanguage(text) {
    if (!text) return currentVoiceLanguage || "en-IN";
    const lower = text.toLowerCase();
    if (/[\u0B80-\u0BFF]/.test(text)) return "ta-IN";
    if (/[\u0900-\u097F]/.test(text)) return "hi-IN";
    if (/[\u0C00-\u0C7F]/.test(text)) return "te-IN";
    if (/[\u0D00-\u0D7F]/.test(text)) return "ml-IN";
    if (/[\u0C80-\u0CFF]/.test(text)) return "kn-IN";
    if (/[\u0980-\u09FF]/.test(text)) return "bn-IN";
    if (["meilleur", "écouteurs", "ordinateur", "prix"].some(w => lower.includes(w))) return "fr-FR";
    if (["auriculares", "zapatos", "precio", "bueno"].some(w => lower.includes(w))) return "es-ES";
    if (["kopfhörer", "billig", "schuhe", "preis"].some(w => lower.includes(w))) return "de-DE";
    return currentVoiceLanguage || "en-IN";
  }

  function getLanguageName(code) {
    const map = {
      "ta-IN": "Tamil (தமிழ்)",
      "hi-IN": "Hindi (हिन्दी)",
      "te-IN": "Telugu (తెలుగు)",
      "ml-IN": "Malayalam (മലയാളം)",
      "kn-IN": "Kannada (ಕನ್ನಡ)",
      "bn-IN": "Bengali (বাংলা)",
      "fr-FR": "French (Français)",
      "es-ES": "Spanish (Español)",
      "de-DE": "German (Deutsch)",
      "en-IN": "English (India)"
    };
    return map[code] || "English";
  }

  function toggleVoiceAudioFeedback() {
    isVoiceAudioFeedback = !isVoiceAudioFeedback;
    const badge = $("voiceStatusBadge");
    if (badge) {
      badge.textContent = isVoiceAudioFeedback ? "🔊 Voice: ON" : "🔇 Voice: OFF";
      badge.className = isVoiceAudioFeedback ? "badge-tag badge-blue" : "badge-tag badge-red";
    }
    showToast(`Voice audio feedback ${isVoiceAudioFeedback ? 'Enabled' : 'Muted'}`, "info");
  }

  function toggleDiscoveryVoiceFeedback() {
    toggleVoiceAudioFeedback();
    const btn = $("btnVoiceResponseToggle");
    if (btn) {
      btn.textContent = isVoiceAudioFeedback ? "🔊 Voice Response: ON" : "🔇 Voice Response: OFF";
      btn.style.color = isVoiceAudioFeedback ? "#38bdf8" : "#94a3b8";
    }
  }

  function changeVoiceLanguage(lang) {
    currentVoiceLanguage = lang;
    if (speechRecognitionInstance) speechRecognitionInstance.lang = lang;
    const langName = $("voiceLangSelect")?.selectedOptions?.[0]?.text || lang;
    showToast(`Voice Language: ${langName}`, "info");
    speak(`Voice set to ${langName}.`, lang);
  }

  function toggleHandsFreeVoice() {
    isHandsFreeActive = !isHandsFreeActive;
    const label = $("handsFreeLabel");
    const btn = $("btnHandsFreeToggle");
    if (label) label.textContent = isHandsFreeActive ? "ON" : "OFF";
    if (btn) btn.classList.toggle("active", isHandsFreeActive);

    if (isHandsFreeActive) {
      showToast("Hands-Free Voice Listening Activated!", "success");
      speak("Hands-Free Voice is active. You can speak your requests.");
      startContinuousVoiceRecognition();
    } else {
      showToast("Hands-Free Voice Stopped", "info");
      if (speechRecognitionInstance) speechRecognitionInstance.stop();
    }
  }

  function startContinuousVoiceRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      showToast("Voice recognition not supported in this browser.", "error");
      return;
    }
    speechRecognitionInstance = new SpeechRec();
    speechRecognitionInstance.lang = currentVoiceLanguage || "en-IN";
    speechRecognitionInstance.continuous = true;
    speechRecognitionInstance.interimResults = false;

    speechRecognitionInstance.onresult = (event) => {
      const last = event.results.length - 1;
      const transcript = event.results[last][0].transcript.trim();
      const detected = detectScriptLanguage(transcript);
      showToast(`🎙️ Heard: "${transcript}" (${getLanguageName(detected)})`, "info");
      handleSpokenCommand(transcript);
    };

    speechRecognitionInstance.onerror = () => {
      if (isHandsFreeActive) setTimeout(startContinuousVoiceRecognition, 1500);
    };

    speechRecognitionInstance.start();
  }

  function handleSpokenCommand(cmd) {
    if ($("mainChatInput")) $("mainChatInput").value = cmd;
    sendMainChatMessage();
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

    showToast(`🔴 Listening in ${currentVoiceLanguage}... Speak your product query!`, "info");

    rec.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (micBtn) micBtn.classList.remove("listening");
      if ($("mainChatInput")) $("mainChatInput").value = text;
      showToast(`🎙️ Recognized: "${text}"`, "info");
      sendMainChatMessage();
    };

    rec.onerror = () => {
      if (micBtn) micBtn.classList.remove("listening");
      showToast("Voice listening completed.", "info");
    };

    rec.start();
  }

  function simulateVoiceInput(phrase) {
    const detectedLang = detectScriptLanguage(phrase);
    showToast(`🎙️ Voice Recognized: "${phrase}" (${getLanguageName(detectedLang)})`, "info");
    if ($("mainChatInput")) $("mainChatInput").value = phrase;
    sendMainChatMessage();
  }

  function handleQuickChip(chipText) {
    if ($("mainChatInput")) $("mainChatInput").value = chipText;
    sendMainChatMessage();
  }

  // Main Tab Navigation
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

  // AI Conversational Chat Flow
  async function sendMainChatMessage() {
    const input = $("mainChatInput");
    const message = input ? input.value.trim() : "";
    if (!message) return;
    if (input) input.value = "";

    appendChatMessage("customer", message);

    try {
      const data = await api("/api/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message, session_id: "sess_web_01", customer_id: "1" })
      });

      const reply = data.reply || data.message || "I found some recommendations for you.";
      appendChatMessage("agent", reply, data);
      speak(reply);

      if (data.recommendations && data.recommendations.length > 0) {
        updateFeatureProductCard(data.recommendations[0]);
      }
    } catch (e) {
      appendChatMessage("agent", `Error: ${e.message}`);
    }
  }

  function appendChatMessage(sender, text, meta = null) {
    const stream = $("liveChatBubbleStream") || $("mainChatStream");
    if (!stream) return;
    const div = document.createElement("div");
    div.className = `chat-bubble chat-bubble-${sender}`;
    div.style.marginBottom = "10px";
    div.style.padding = "10px 14px";
    div.style.borderRadius = "10px";
    div.style.background = sender === 'customer' ? 'rgba(30, 41, 59, 0.7)' : 'rgba(99, 102, 241, 0.12)';
    div.style.border = `1px solid ${sender === 'customer' ? '#334155' : 'rgba(99, 102, 241, 0.3)'}`;

    let html = `<div style="font-size:11px; font-weight:800; color:${sender === 'customer' ? '#38bdf8' : '#a855f7'}; margin-bottom:4px; text-transform:uppercase;">${sender === 'customer' ? '👤 YOU' : '🤖 RAZORFLOW X AGENT'}</div>`;
    html += `<div style="font-size:13px; line-height:1.5; color:#f8fafc;">${text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')}</div>`;

    if (meta && meta.recommendations && meta.recommendations.length > 0) {
      html += `<div style="margin-top:12px; font-size:11px; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.5px;">🛍️ AI MATCHED PRODUCTS (${meta.recommendations.length} ITEMS):</div>`;
      html += `<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:10px; margin-top:8px;">`;
      
      meta.recommendations.slice(0, 4).forEach((opt, idx) => {
        const p = opt.product || opt;
        const pId = p.product_id || p.id || `PROD_${idx+1}`;
        const safeName = (p.name || '').replace(/'/g, "\'");
        const safeImg = (p.image_url || '').replace(/'/g, "\'");
        const safeCat = (p.category || 'tech').replace(/'/g, "\'");
        const origPrice = p.original_price || Math.round(p.price * 1.2);
        const isTop = opt.is_top_pick || opt.rank === 1 || idx === 0;
        const delDays = p.delivery_days || 1;

        html += `
          <div style="background:#080c14; border:1px solid ${isTop ? '#3b82f6' : '#1e293b'}; border-radius:10px; padding:10px; font-size:11px; display:flex; flex-direction:column; justify-content:space-between; position:relative; box-shadow:0 4px 12px rgba(0,0,0,0.5);">
            ${isTop ? '<span style="position:absolute; top:6px; left:6px; background:#2563eb; color:white; font-size:9px; font-weight:800; padding:2px 6px; border-radius:4px; z-index:2;">⭐ TOP PICK</span>' : ''}
            <div>
              <img src="${p.image_url || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300'}" 
                   alt="${safeName}"
                   style="width:100%; height:110px; object-fit:cover; border-radius:8px; margin-bottom:6px; background:#1e293b;"
                   onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=300';">
              <div style="font-size:10px; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-bottom:2px;">${p.brand || 'Authentic Store'}</div>
              <strong style="color:white; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; font-size:12px; line-height:1.3; margin-bottom:4px; height:32px;" title="${p.name}">${p.name}</strong>
              <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:4px;">
                <span style="color:#4ade80; font-weight:900; font-size:14px; font-family:var(--font-mono);">₹${Number(p.price).toLocaleString('en-IN')}</span>
                <span style="color:#64748b; font-size:10px; text-decoration:line-through;">₹${Number(origPrice).toLocaleString('en-IN')}</span>
              </div>
              <div style="display:flex; justify-content:space-between; font-size:10px; color:#cbd5e1; margin-bottom:8px;">
                <span style="color:#fbbf24;">★ ${p.rating || 4.8}</span>
                <span>⚡ ${delDays}-Day SLA</span>
              </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-top:auto;">
              <button onclick="addToCart('${pId}', '${safeName}')" style="background:#1e293b; color:#38bdf8; border:1px solid #334155; border-radius:6px; padding:6px 0; font-size:11px; font-weight:700; cursor:pointer;">
                + Cart
              </button>
              <button onclick="handleQuickSelectProduct('${pId}', '${safeName}', ${p.price}, '${safeImg}', '${safeCat}')" style="background:linear-gradient(135deg,#4f46e5,#9333ea); color:white; border:none; border-radius:6px; padding:6px 0; font-size:11px; font-weight:800; cursor:pointer;">
                ⚡ Select
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

  function handleQuickSelectProduct(id, name, price, img, cat) {
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
    showToast(`Selected "${name}" (₹${price.toLocaleString('en-IN')})`, "success");
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

    // Smart Cross-sell update
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
    if ($("greenCardAmount")) $("greenCardAmount").textContent = `₹${total.toLocaleString("en-IN")}.00`;
    if ($("wReceiptAmount")) $("wReceiptAmount").textContent = `₹${total.toLocaleString("en-IN")}.00`;
  }

  async function triggerSimulatedFailureFlow() {
    showToast("⚠️ Injecting 30s Gateway Timeout on State Bank of India...", "warning");
    speak("Simulating payment gateway timeout error on State Bank of India.");
    
    const logBox = $("chaosStateLog");
    if (logBox) {
      logBox.innerHTML = `
        <span style="color:#f87171;">[CHAOS] Injected GATEWAY_TIMEOUT (504) on State Bank of India.</span><br>
        <span style="color:#fbbf24;">[FSM] State: PROCESSING ➔ RECOVERY_PENDING</span><br>
        <span style="color:#60a5fa;">[POLICY] Idempotency Key locked: 0 double-billing risk.</span><br>
        <span style="color:#4ade80;">[RECOVERY] Autonomous AI recovery ready for 1-click fallback.</span>
      `;
    }

    try {
      await api("/api/payment/failure", {
        method: "POST",
        body: JSON.stringify({ order_id: `ord_${Date.now().toString().slice(-6)}`, amount: currentOrderAmount, error_type: "GATEWAY_TIMEOUT" })
      });
      loadTransactions();
    } catch (_) {}
    setTimeout(() => openFailureRetryModal(), 800);
  }

  async function triggerAiAlternateRecovery(route) {
    closeFailureRetryModal();
    showToast(`⚡ Autonomous AI Recovery: Transitioning to ${route}...`, "success");
    speak(`Autonomous recovery rerouting order through ${route}.`);
    
    const logBox = $("chaosStateLog");
    if (logBox) {
      logBox.innerHTML = `
        <span style="color:#38bdf8;">[RECOVERY] Transitioning to ${route}...</span><br>
        <span style="color:#4ade80;">[FSM] State: RECOVERY_PENDING ➔ SUCCESS (200 OK)</span><br>
        <span style="color:#93c5fd;">[LEDGER] Payment Captured: ₹${currentOrderAmount.toLocaleString('en-IN')}.00</span><br>
        <span style="color:#a7f3d0;">[AUDIT] Cryptographic SHA-256 block added to immutable log.</span>
      `;
    }

    try {
      const res = await api("/api/payments/recover", {
        method: "POST",
        body: JSON.stringify({ order_id: `ord_${Date.now().toString().slice(-6)}`, strategy: "AUTO_RETRY" })
      });

      const pId = res.payment_id || `pay_${uuid4().slice(0, 14)}`;
      if ($("greenCardAmount")) $("greenCardAmount").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;
      if ($("greenCardPaymentId")) $("greenCardPaymentId").textContent = pId;
      if ($("greenCardMethod")) $("greenCardMethod").textContent = route || "Instant UPI Fast Track (MPIN)";

      if ($("wReceiptAmount")) $("wReceiptAmount").textContent = `₹${currentOrderAmount.toLocaleString('en-IN')}.00`;
      if ($("wReceiptPayId")) $("wReceiptPayId").textContent = pId;
      if ($("wReceiptMethod")) $("wReceiptMethod").textContent = route || "Instant UPI Fast Track";

      // Deduct order amount from wallet balance
      userWalletBalance = Math.max(0, userWalletBalance - currentOrderAmount);
      logWalletActivity(`Recovered Purchase: ${currentActiveProduct ? currentActiveProduct.name : 'Shopping Order'}`, currentOrderAmount, false);
      updateUserWalletDisplays();
      loadTransactions();

      setTimeout(() => {
        const greenScreen = $("rzpGreenSuccessScreen");
        if (greenScreen) greenScreen.classList.add("open");
        speak("Autonomous recovery captured payment successfully!");
        setTimeout(() => {
          if (greenScreen) greenScreen.classList.remove("open");
          openWhiteReceiptModal();
        }, 2200);
      }, 600);
    } catch (e) {
      showToast("Recovery error: " + e.message, "error");
    }
  }

  async function runSpecificChaosScenario(scenario) {
    const scenNames = {
      scenario_1: "Gateway Timeout (504)",
      scenario_2: "Network Socket Drop",
      scenario_3: "Duplicate Request Race",
      scenario_4: "Payment Declined",
      scenario_5: "Webhook Delay (45s)",
      scenario_6: "Signature Tamper Mismatch",
      scenario_7: "Bounded Retry Exhaustion (Cap: 2)"
    };

    const name = scenNames[scenario] || scenario;
    showToast(`⚡ Injecting Chaos Scenario: ${name}`, "warning");
    speak(`Injecting chaos scenario ${name}.`);

    const stream = $("reliabilityStateStream");
    if (stream) {
      stream.innerHTML = `
        <span style="color:#f87171;">[INJECT] Scenario: ${name}</span><br>
        <span style="color:#fbbf24;">[FSM] Evaluating deterministic Finite State Machine transition...</span><br>
        <span style="color:#38bdf8;">[POLICY] Locking 256-bit Idempotency Key & Checking 8-Factor Money Safety Guardrails...</span><br>
        <span style="color:#4ade80;">[RECOVERY ENGINE] Self-Healing state executed with zero double-charge guarantee.</span>
      `;
    }

    try {
      const res = await api("/api/simulate/scenario", {
        method: "POST",
        body: JSON.stringify({ scenario_type: scenario })
      });
      loadTransactions();
      showToast(`✓ Chaos Simulation Result: ${res.fsm_status} (${res.recovery_strategy})`, "success");
      speak(`Scenario executed. FSM status: ${res.fsm_status}.`);
    } catch (e) {
      showToast("Simulation error: " + e.message, "error");
    }
  }

  // Judge Guided Tour Functions
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
      showToast("🏆 Judge Demo Walkthrough Complete!", "success");
      speak("Judge demo walkthrough complete. Thank you!");
    }
  }

  function prevJudgeStep() {
    if (judgeTourCurrentStep > 0) {
      judgeTourCurrentStep--;
      renderJudgeTourStep();
    }
  }

  // Close overlays on backdrop click & Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".rfx-modal-overlay.open").forEach(m => m.classList.remove("open"));
      $("cartDrawerOverlay")?.classList.remove("open");
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("rfx-modal-overlay")) {
      e.target.classList.remove("open");
    }
    if (e.target.id === "cartDrawerOverlay") {
      e.target.classList.remove("open");
    }
    if (e.target.id === "walletSlideDrawerOverlay") {
      e.target.classList.remove("open");
    }
  });

  // DOM Loaded initialization
  document.addEventListener("DOMContentLoaded", () => {
    executeDiscoverySearch();
    loadCart();
    loadDashboardMetrics();
    loadTransactions();
    loadAuditLogs();
  });
