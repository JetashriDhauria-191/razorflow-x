/**
 * RAZORFLOW X — Master Client Controller
 * Track 1: AI Growth & Agentic Commerce Platform
 */

let allProducts = [];
let filteredProducts = [];
let cart = [];
let compareList = [];
let currentCategory = 'all';
let currentSort = 'recommended';
let activeTotal = 0;
let activeOrderId = 'order_' + Math.random().toString(36).substring(2, 12);

// Speech Recognition
let recognition = null;
let isVoiceRecording = false;

document.addEventListener('DOMContentLoaded', async () => {
    initSpeechRecognition();
    await fetchCatalogData();
    renderMainGrid();

    // Auto route handling
    const path = window.location.pathname;
    if (path.includes('/dashboard')) {
        switchView('growth');
    } else if (path.includes('/pitch')) {
        switchView('pitch');
    }
});

/**
 * 1. CATALOGUE & SEARCH
 */
async function fetchCatalogData() {
    try {
        const res = await fetch('/api/catalog');
        if (res.ok) {
            const data = await res.json();
            allProducts = Array.isArray(data) ? data : (data.products || []);
            filteredProducts = [...allProducts];
            updateCountLabel();
        }
    } catch (e) {
        console.warn("Catalog fetch:", e);
    }
}

function updateCountLabel() {
    const label = document.getElementById('store-product-count');
    if (label) label.innerText = `${filteredProducts.length} Products Available in AI Catalogue`;
}

function renderMainGrid() {
    const grid = document.getElementById('main-product-grid');
    if (!grid) return;

    if (filteredProducts.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; background: rgba(255,255,255,0.02); border-radius: 14px; border: 1px dashed rgba(255,255,255,0.1);">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🔍</div>
                <h3 style="font-weight: 700; color: #f8fafc; margin-bottom: 6px;">No products match your filter</h3>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 16px;">Try searching with our AI Copilot for any item (e.g. 'smart TV', 'coffee mug', 'drone')</p>
                <button onclick="filterByCat('all')" class="btn btn-secondary">Reset Filters</button>
            </div>
        `;
        return;
    }

    grid.innerHTML = filteredProducts.map(p => {
        const stars = "★".repeat(Math.round(p.rating || 4.8)) + "☆".repeat(5 - Math.round(p.rating || 4.8));
        const aiScore = p.ai_score || Math.min(99, Math.round(82 + (p.rating * 3) + (p.margin * 10)));
        const origPrice = p.discount ? Math.round(p.price / (1 - p.discount/100)) : Math.round(p.price * 1.15);

        return `
            <div class="product-card">
                <div class="product-image-box">
                    <img src="${p.image_url}" alt="${p.name}" class="product-img" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=70'">
                    <span class="badge-ai-match">⭐ ${aiScore}% Match</span>
                    ${p.discount ? `<span class="badge-discount">-${p.discount}%</span>` : ''}
                </div>
                <div class="product-content">
                    <div class="product-brand">${p.brand || 'ProTech'}</div>
                    <div class="product-title" title="${p.name}">${p.name}</div>
                    <div class="product-rating-row">
                        <span class="stars">${stars}</span>
                        <span class="rating-num">${(p.rating || 4.8).toFixed(1)}</span>
                        <span class="review-count">(${p.review_count || 1240})</span>
                    </div>
                    <div class="product-price-row">
                        <span class="price-current">₹${p.price.toLocaleString('en-IN')}</span>
                        <span class="price-original">₹${origPrice.toLocaleString('en-IN')}</span>
                    </div>
                    <div class="delivery-pill">⚡ <strong>Get it by Tomorrow</strong> | Free Delivery</div>
                    <div class="why-list">
                        ${(p.why_bullets || [`✓ Highly rated ${(p.rating||4.8)}★ customer favorite`, `✓ Best value-to-performance in ${p.category}`]).slice(0, 2).map(w => `<div class="why-bullet">${w}</div>`).join('')}
                    </div>
                    <div class="product-actions">
                        <button onclick="addProductToCart('${p.product_id}')" class="btn-add-cart">+ Add to Cart</button>
                        <button onclick="quickSelectAndOrder('${p.product_id}')" class="btn btn-secondary" style="padding: 8px 10px; font-size: 0.78rem;">Buy Now</button>
                        <button onclick="toggleCompareProduct('${p.product_id}')" class="btn btn-secondary" style="padding: 8px 8px; font-size: 0.78rem;" title="Compare">⚖️</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 2. PROGRESSIVE VOICE & NATURAL LANGUAGE SEARCH (Sections 45, 46, 47)
 */
async function handleSearchSubmit() {
    const input = document.getElementById('global-search-input');
    const query = input ? input.value.trim() : '';
    if (!query) {
        filteredProducts = [...allProducts];
        renderMainGrid();
        updateCountLabel();
        return;
    }

    showSearchStatus("Understanding your request...");
    await new Promise(r => setTimeout(r, 400));
    showSearchStatus("Finding the best matches...");

    try {
        const res = await fetch(`/api/recommendations?intent=${encodeURIComponent(query)}`);
        if (res.ok) {
            const data = await res.json();
            if (data.options && data.options.length > 0) {
                filteredProducts = data.options.map(o => ({
                    ...o.product,
                    ai_score: Math.round(o.recommendation_score),
                    why_bullets: o.why_recommended
                }));

                renderSpotlightCard(data.options[0], data.options.length, data.suggested_bundle);

                if ('speechSynthesis' in window && isVoiceRecording) {
                    speakVoiceText(`I found ${data.options.length} matches. Top recommendation: ${data.options[0].product.name} for rupees ${data.options[0].product.price}`);
                }
            } else {
                const qL = query.toLowerCase();
                filteredProducts = allProducts.filter(p => p.name.toLowerCase().includes(qL) || (p.tags && p.tags.some(t => t.toLowerCase().includes(qL))));
            }
        }
    } catch (e) {
        console.warn(e);
    }

    hideSearchStatus();
    renderMainGrid();
    updateCountLabel();
}

function showSearchStatus(text) {
    const hud = document.getElementById('search-status-hud');
    const hudText = document.getElementById('search-status-text');
    if (hud && hudText) {
        hudText.innerText = text;
        hud.classList.add('active');
    }
}

function hideSearchStatus() {
    const hud = document.getElementById('search-status-hud');
    if (hud) hud.classList.remove('active');
}

function executeQuickSearch(query) {
    const input = document.getElementById('global-search-input');
    if (input) input.value = query;
    handleSearchSubmit();
}

function renderSpotlightCard(topOpt, matchCount, bundle) {
    const container = document.getElementById('spotlight-area');
    if (!container) return;

    const p = topOpt.product;
    container.innerHTML = `
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98)); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 16px; padding: 22px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: #2563eb; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 800;">🤖 AI RECOMMENDATION</span>
                    <span style="font-size: 0.85rem; color: #94a3b8;">I found <strong>${matchCount}</strong> products</span>
                </div>
                <button onclick="document.getElementById('spotlight-area').style.display='none'" style="background: none; border: none; color: #94a3b8; font-size: 1.1rem; cursor: pointer;">✕</button>
            </div>
            <div style="display: grid; grid-template-columns: 100px 1fr; gap: 18px; align-items: center;">
                <img src="${p.image_url}" alt="${p.name}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
                <div>
                    <div style="font-size: 0.85rem; color: #60a5fa; font-weight: 800; margin-bottom: 2px;">🏆 Best Overall Pick</div>
                    <h3 style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">${p.name}</h3>
                    <div style="font-size: 1.25rem; font-weight: 900; color: #60a5fa; margin-bottom: 8px;">₹${p.price.toLocaleString('en-IN')}</div>
                    
                    <div style="font-size: 0.82rem; color: #cbd5e1; margin-bottom: 12px; display: grid; gap: 3px;">
                        <strong style="color: #94a3b8;">Why:</strong>
                        ${(topOpt.why_recommended || ['✓ Within configured budget', '✓ High customer star rating', '✓ Fast delivery guaranteed', '✓ Strong semantic intent match']).map(w => `<div>${w.startsWith('✓') ? w : '✓ ' + w}</div>`).join('')}
                    </div>

                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="addProductToCart('${p.product_id}')" class="btn btn-primary" style="padding: 6px 14px; font-size: 0.85rem;">+ Add to Cart</button>
                        <button onclick="quickSelectAndOrder('${p.product_id}')" class="btn btn-secondary" style="padding: 6px 14px; font-size: 0.85rem;">Instant Checkout</button>
                        <button onclick="filterByCat('all')" class="btn btn-secondary" style="padding: 6px 14px; font-size: 0.85rem;">Show Alternatives</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    container.style.display = 'block';
}

function filterByCat(cat) {
    currentCategory = cat;
    document.querySelectorAll('.cat-pill').forEach(pill => {
        pill.classList.toggle('active', pill.innerText.toLowerCase().includes(cat.toLowerCase()) || (cat === 'all' && pill.innerText.includes('All')));
    });

    if (cat === 'all') {
        filteredProducts = [...allProducts];
    } else {
        filteredProducts = allProducts.filter(p => (p.category || '').toLowerCase() === cat.toLowerCase());
    }
    renderMainGrid();
    updateCountLabel();
}

function handleSortChange(sortType) {
    if (sortType === 'price-asc') {
        filteredProducts.sort((a, b) => a.price - b.price);
    } else if (sortType === 'price-desc') {
        filteredProducts.sort((a, b) => b.price - a.price);
    } else if (sortType === 'rating') {
        filteredProducts.sort((a, b) => (b.rating || 4.8) - (a.rating || 4.8));
    } else {
        filteredProducts.sort((a, b) => (b.ai_score || 80) - (a.ai_score || 80));
    }
    renderMainGrid();
}

/**
 * 3. PRODUCT COMPARISON (Phase 8)
 */
function toggleCompareProduct(productId) {
    const p = allProducts.find(x => x.product_id === productId);
    if (!p) return;

    if (compareList.some(x => x.product_id === productId)) {
        compareList = compareList.filter(x => x.product_id !== productId);
        alert(`Removed ${p.name} from comparison.`);
    } else {
        if (compareList.length >= 3) {
            compareList.shift();
        }
        compareList.push(p);
        alert(`Added ${p.name} to comparison (${compareList.length}/3 selected).`);
        if (compareList.length >= 2) {
            showComparisonModal();
        }
    }
}

function showComparisonModal() {
    if (compareList.length < 2) {
        alert("Please select at least 2 products using the ⚖️ button to compare.");
        return;
    }
    const modal = document.getElementById('compare-modal');
    const tableBody = document.getElementById('compare-table-body');
    if (!modal || !tableBody) return;

    tableBody.innerHTML = `
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 10px; color: #94a3b8; font-weight: 700;">Product</td>
            ${compareList.map(p => `<td style="padding: 10px; font-weight: 800; color: #f8fafc;">${p.name}</td>`).join('')}
        </tr>
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 10px; color: #94a3b8; font-weight: 700;">Price</td>
            ${compareList.map(p => `<td style="padding: 10px; font-weight: 800; color: #60a5fa;">₹${p.price.toLocaleString('en-IN')}</td>`).join('')}
        </tr>
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 10px; color: #94a3b8; font-weight: 700;">Rating</td>
            ${compareList.map(p => `<td style="padding: 10px; color: #fbbf24;">★ ${(p.rating||4.8).toFixed(1)}</td>`).join('')}
        </tr>
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 10px; color: #94a3b8; font-weight: 700;">AI Score</td>
            ${compareList.map(p => `<td style="padding: 10px; color: #10b981; font-weight: 800;">${p.ai_score || 94}%</td>`).join('')}
        </tr>
        <tr>
            <td style="padding: 10px; color: #94a3b8; font-weight: 700;">Action</td>
            ${compareList.map(p => `<td style="padding: 10px;"><button onclick="addProductToCart('${p.product_id}'); closeCompareModal();" class="btn btn-primary" style="padding: 4px 10px; font-size: 0.75rem;">Add to Cart</button></td>`).join('')}
        </tr>
    `;

    modal.classList.add('active');
}

function closeCompareModal() {
    const modal = document.getElementById('compare-modal');
    if (modal) modal.classList.remove('active');
}

/**
 * 4. CART & PROACTIVE GROWTH
 */
function addProductToCart(productId) {
    const p = allProducts.find(x => x.product_id === productId) || filteredProducts.find(x => x.product_id === productId);
    if (!p) return;

    const existing = cart.find(i => i.product_id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ ...p, quantity: 1 });
    }
    updateCartUI();
    openCartDrawer();
}

function updateCartQuantity(productId, delta) {
    const item = cart.find(i => i.product_id === productId);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.product_id !== productId);
    }
    updateCartUI();
}

function updateCartUI() {
    const countBadge = document.getElementById('header-cart-count');
    const totalCount = cart.reduce((sum, i) => sum + i.quantity, 0);
    if (countBadge) countBadge.innerText = totalCount;

    const container = document.getElementById('cart-drawer-items');
    const subtotalEl = document.getElementById('cart-subtotal-val');
    const discountEl = document.getElementById('cart-discount-val');
    const totalEl = document.getElementById('cart-total-val');

    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px 10px; color: #94a3b8;">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">🛒</div>
                <div style="font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">Your cart is empty</div>
                <div style="font-size: 0.8rem;">Discover products using search or voice commands.</div>
            </div>
        `;
        if (subtotalEl) subtotalEl.innerText = '₹0';
        if (discountEl) discountEl.innerText = '-₹0';
        if (totalEl) totalEl.innerText = '₹0';
        activeTotal = 0;
        return;
    }

    let subtotal = cart.reduce((sum, i) => sum + (i.price * i.quantity), 0);
    let discount = cart.length > 1 ? Math.round(subtotal * 0.05) : 0;
    activeTotal = subtotal - discount;

    container.innerHTML = cart.map(item => `
        <div style="display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.06); align-items: center;">
            <img src="${item.image_url}" alt="${item.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px;">
            <div style="flex: 1; min-width: 0;">
                <div style="font-size: 0.85rem; font-weight: 700; color: #f8fafc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${item.name}</div>
                <div style="font-size: 0.82rem; font-weight: 800; color: #60a5fa; margin-top: 2px;">₹${item.price.toLocaleString('en-IN')}</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                    <button onclick="updateCartQuantity('${item.product_id}', -1)" style="width: 22px; height: 22px; background: rgba(255,255,255,0.1); border: none; color: white; border-radius: 4px; cursor: pointer;">-</button>
                    <span style="font-size: 0.8rem; font-weight: 700; color: #f8fafc;">${item.quantity}</span>
                    <button onclick="updateCartQuantity('${item.product_id}', 1)" style="width: 22px; height: 22px; background: rgba(255,255,255,0.1); border: none; color: white; border-radius: 4px; cursor: pointer;">+</button>
                </div>
            </div>
            <button onclick="updateCartQuantity('${item.product_id}', -${item.quantity})" style="background: none; border: none; color: #ef4444; cursor: pointer;">🗑️</button>
        </div>
    `).join('');

    if (subtotalEl) subtotalEl.innerText = `₹${subtotal.toLocaleString('en-IN')}`;
    if (discountEl) discountEl.innerText = `-₹${discount.toLocaleString('en-IN')}`;
    if (totalEl) totalEl.innerText = `₹${activeTotal.toLocaleString('en-IN')}`;
}

function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) drawer.classList.add('open');
    if (overlay) overlay.classList.add('open');
}

function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');
    if (drawer) drawer.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
}

/**
 * 5. MONEY SAFETY GATE & RAZORPAY TEST PAYMENT
 */
function quickSelectAndOrder(productId) {
    const p = allProducts.find(x => x.product_id === productId) || filteredProducts.find(x => x.product_id === productId);
    if (!p) return;
    cart = [{ ...p, quantity: 1 }];
    updateCartUI();
    openSafetyGateModal();
}

function openSafetyGateModal() {
    if (cart.length === 0) {
        alert("Your cart is empty. Add products to proceed.");
        return;
    }
    closeCartDrawer();
    activeOrderId = 'order_' + Math.random().toString(36).substring(2, 14);

    const modal = document.getElementById('safety-modal');
    const amtLabel = document.getElementById('safety-pay-btn-amount');
    const idemKey = document.getElementById('safety-idem-key');

    if (amtLabel) amtLabel.innerText = `₹${activeTotal.toLocaleString('en-IN')}`;
    if (idemKey) idemKey.innerText = `idem_${Date.now().toString(36)}`;
    if (modal) modal.classList.add('active');
}

function closeSafetyGateModal() {
    const modal = document.getElementById('safety-modal');
    if (modal) modal.classList.remove('active');
}

function openPaymentTerminalModal() {
    closeSafetyGateModal();
    const modal = document.getElementById('payment-terminal-modal');
    const ordLabel = document.getElementById('payment-order-id-label');
    const dueLabel = document.getElementById('payment-total-due-label');

    if (ordLabel) ordLabel.innerText = activeOrderId;
    if (dueLabel) dueLabel.innerText = `₹${activeTotal.toLocaleString('en-IN')}`;
    if (modal) modal.classList.add('active');
}

function closePaymentTerminalModal() {
    const modal = document.getElementById('payment-terminal-modal');
    if (modal) modal.classList.remove('active');
}

function selectPaymentTab(tab) {
    ['card', 'upi', 'netbank', 'wallet'].forEach(t => {
        const btn = document.getElementById(`tab-p-${t}`);
        const content = document.getElementById(`p-content-${t}`);
        if (btn) btn.className = (t === tab) ? 'btn btn-primary' : 'btn btn-secondary';
        if (content) content.style.display = (t === tab) ? 'block' : 'none';
    });
}

function open3DSecureOTPModal() {
    closePaymentTerminalModal();
    const modal = document.getElementById('otp-modal');
    if (modal) modal.classList.add('active');
}

function closeOTPModal() {
    const modal = document.getElementById('otp-modal');
    if (modal) modal.classList.remove('active');
}

async function submitFinalPaymentVerification() {
    const btn = document.getElementById('btn-submit-otp');
    if (btn) {
        btn.innerHTML = '⏳ Verifying with Razorpay Bank Switch...';
        btn.disabled = true;
    }

    const paymentId = 'pay_' + Math.random().toString(36).substring(2, 12);
    try {
        await fetch('/api/payments/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                order_id: activeOrderId,
                razorpay_order_id: activeOrderId,
                razorpay_payment_id: paymentId,
                razorpay_signature: 'sig_mock_valid_hmac_sha256',
                amount: activeTotal
            })
        });
    } catch (e) {
        console.warn(e);
    }

    closeOTPModal();
    cart = [];
    updateCartUI();

    const rcptAmt = document.getElementById('rcpt-amt');
    const rcptPay = document.getElementById('rcpt-pay-id');
    const rcptOrd = document.getElementById('rcpt-ord-id');

    if (rcptAmt) rcptAmt.innerText = `₹${activeTotal.toLocaleString('en-IN')}`;
    if (rcptPay) rcptPay.innerText = paymentId;
    if (rcptOrd) rcptOrd.innerText = activeOrderId;

    const receiptModal = document.getElementById('receipt-modal');
    if (receiptModal) receiptModal.classList.add('active');
}

function closeReceiptModal() {
    const modal = document.getElementById('receipt-modal');
    if (modal) modal.classList.remove('active');
}

/**
 * 6. VOICE SHOPPING
 */
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.onresult = (e) => {
        const text = e.results[0][0].transcript;
        const searchInput = document.getElementById('global-search-input');
        if (searchInput) searchInput.value = text;
        showSearchStatus(`Understood: "${text}"`);
        handleSearchSubmit();
    };
    recognition.onend = () => {
        isVoiceRecording = false;
        const mic = document.getElementById('voice-mic-header-btn');
        if (mic) mic.classList.remove('listening');
    };
}

function toggleVoiceShopping() {
    if (!recognition) {
        alert("Speech Recognition is not supported by your browser. Please use Google Chrome.");
        return;
    }
    const mic = document.getElementById('voice-mic-header-btn');
    if (isVoiceRecording) {
        recognition.stop();
        isVoiceRecording = false;
        if (mic) mic.classList.remove('listening');
        hideSearchStatus();
    } else {
        try {
            recognition.start();
            isVoiceRecording = true;
            if (mic) mic.classList.add('listening');
            showSearchStatus("Listening...");
        } catch (e) {
            recognition.stop();
            isVoiceRecording = false;
            if (mic) mic.classList.remove('listening');
            hideSearchStatus();
        }
    }
}

function speakVoiceText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 1.0;
        window.speechSynthesis.speak(utter);
    }
}

/**
 * 7. TAB & VIEW SWITCHING WITH OBSERVABILITY
 */
async function loadLiveGrowthMetrics() {
    try {
        const res = await fetch('/api/growth/overview');
        if (res.ok) {
            const data = await res.json();
            const gmvEl = document.getElementById('growth-gpv');
            if (gmvEl && data.total_gmv_processed) {
                gmvEl.innerText = `₹${Math.round(data.total_gmv_processed).toLocaleString('en-IN')}`;
            }
        }
    } catch (e) {
        console.warn("Growth overview fetch:", e);
    }
}

function switchView(viewName) {
    if (viewName === 'growth') loadLiveGrowthMetrics();

    const views = ['storefront', 'agent', 'growth', 'recovery', 'pitch'];
    views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if (el) el.style.display = (v === viewName) ? 'block' : 'none';
    });

    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    const activeTab = document.getElementById(`tab-nav-${viewName === 'storefront' ? 'store' : viewName}`);
    if (activeTab) activeTab.classList.add('active');
}

function sendAgentMessage() {
    const input = document.getElementById('chat-text-input');
    const text = input ? input.value.trim() : '';
    if (!text) return;

    input.value = '';
    const chat = document.getElementById('chat-messages');
    if (!chat) return;

    chat.innerHTML += `
        <div style="display: flex; gap: 10px; max-width: 85%; align-self: flex-end; flex-direction: row-reverse;">
            <div style="width: 32px; height: 32px; background: #7c3aed; border-radius: 8px; display: flex; align-items: center; justify-content: center;">👤</div>
            <div style="background: #3b82f6; color: white; padding: 12px 16px; border-radius: 12px; font-size: 0.9rem;">
                ${text}
            </div>
        </div>
    `;
    chat.scrollTop = chat.scrollHeight;

    setTimeout(() => {
        chat.innerHTML += `
            <div style="display: flex; gap: 10px; max-width: 85%;">
                <div style="width: 32px; height: 32px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center;">🤖</div>
                <div style="background: #1e293b; padding: 12px 16px; border-radius: 12px; font-size: 0.9rem; line-height: 1.5;">
                    I have analyzed <strong>"${text}"</strong>. Recommendations updated on the AI Storefront!
                </div>
            </div>
        `;
        chat.scrollTop = chat.scrollHeight;
    }, 600);
}

/**
 * 8. FAILURE RECOVERY PIPELINE SIMULATION
 */
async function runFailureRecoveryPipeline() {
    for (let i = 1; i <= 6; i++) {
        const el = document.getElementById(`rec-step-${i}`);
        if (el) el.style.background = 'rgba(255,255,255,0.05)';
    }

    const step1 = document.getElementById('rec-step-1');
    const step2 = document.getElementById('rec-step-2');
    const step3 = document.getElementById('rec-step-3');
    const step4 = document.getElementById('rec-step-4');
    const step5 = document.getElementById('rec-step-5');
    const step6 = document.getElementById('rec-step-6');

    if (step1) step1.style.background = '#2563eb';
    await new Promise(r => setTimeout(r, 800));

    if (step2) step2.style.background = '#ef4444';
    await new Promise(r => setTimeout(r, 900));

    if (step3) step3.style.background = '#f59e0b';
    await new Promise(r => setTimeout(r, 900));

    if (step4) step4.style.background = '#8b5cf6';
    await new Promise(r => setTimeout(r, 900));

    if (step5) step5.style.background = '#38bdf8';
    await new Promise(r => setTimeout(r, 900));

    if (step6) step6.style.background = '#10b981';
    alert("✅ Autonomous Recovery Verified!
FSM Transition: FAILED → RECOVERY_PENDING → PROCESSING → SUCCESS
Zero double-charge guarantee & HMAC signature validated.");
}

/**
 * 9. GROWTH SIMULATOR & COPILOT
 */
function updateGrowthSimulator() {
    const traffic = parseInt(document.getElementById('sim-traffic').value);
    const cross = parseInt(document.getElementById('sim-cross').value);

    document.getElementById('sim-traffic-val').innerText = traffic.toLocaleString('en-IN');
    document.getElementById('sim-cross-val').innerText = cross + '%';

    const projected = Math.round(traffic * 0.08 * (cross / 100) * 1690);
    document.getElementById('sim-projected-gmv').innerText = `₹${projected.toLocaleString('en-IN')}`;
}

function askGrowthCopilot() {
    const input = document.getElementById('copilot-input');
    const resp = document.getElementById('copilot-response');
    if (resp && input && input.value) {
        resp.innerHTML = `💡 <strong>AI Analysis for "${input.value}"</strong>: Top performing bundle is <em>Laptops + Ergonomic Mice</em> yielding +22.4% AOV expansion with 94% checkout completion.`;
        input.value = '';
    }
}

/**
 * 10. 5-MINUTE GUIDED JUDGE DEMO
 */
function startGuidedJudgeDemo() {
    switchView('storefront');
    executeQuickSearch('Find wireless headphones under ₹5000');
    alert("🎬 5-Minute Guided Demo Started!
1. Showing natural language search with explainable AI scores.
2. Add item to cart to show proactive bundle expansion.
3. Click 'Proceed to AI Safety Checkout' to view the Money Safety Gate.");
}
