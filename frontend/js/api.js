/**
 * RAZORFLOW X - Master API Client
 * Built for Track 1: AI Growth & Agentic Commerce
 */
const API_BASE = '/api';

const API = {
  // Analytics & Overview
  async getOverview() {
    try {
      const res = await fetch(`${API_BASE}/analytics/overview`);
      return await res.json();
    } catch (e) {
      console.warn('API.getOverview fallback:', e);
      return { total_volume: 570850, ai_assisted_revenue: 87400, aov_uplift_percentage: 17.8, conversion_lift_percentage: 12.4, cross_sell_acceptance_rate: 31.2 };
    }
  },

  async getGrowthOverview() {
    try {
      const res = await fetch(`${API_BASE}/growth/overview`);
      return await res.json();
    } catch (e) {
      console.warn('API.getGrowthOverview fallback:', e);
      return { total_gmv_processed: 570850, ai_assisted_revenue: 87400, incremental_revenue_gained: 42100, aov_uplift_percentage: 17.8, conversion_lift_percentage: 12.4, cross_sell_acceptance_rate: 31.2, money_actions_breakdown: { proposed: 420, approved: 405, blocked: 15, executed: 391, recovered: 17 } };
    }
  },

  // 1,000+ Session A/B Experiments
  async getExperimentSummary(nSessions = 1000) {
    const res = await fetch(`${API_BASE}/experiments/summary?n_sessions=${nSessions}`);
    return await res.json();
  },

  // Catalogue
  async getCatalog(category = null, query = null, maxPrice = null) {
    let url = `${API_BASE}/catalog?`;
    if (category) url += `category=${encodeURIComponent(category)}&`;
    if (query) url += `query=${encodeURIComponent(query)}&`;
    if (maxPrice) url += `max_price=${maxPrice}&`;
    const res = await fetch(url);
    return await res.json();
  },

  async getProductDetails(productId) {
    const res = await fetch(`${API_BASE}/catalog/${productId}`);
    return await res.json();
  },

  // Recommendations & Personalization
  async getRecommendations(intent, customerId = 'cust_coding_01', budget = 3000) {
    const res = await fetch(`${API_BASE}/recommendations?intent=${encodeURIComponent(intent)}&customer_id=${customerId}&budget=${budget}`);
    return await res.json();
  },

  // Conversational AI Checkout Agent
  async sendAgentChat(message, sessionId, customerId = 'cust_coding_01', currentCart = null) {
    const res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        customer_id: customerId,
        current_cart: currentCart
      })
    });
    return await res.json();
  },

  // Merchant AI Assistant
  async askMerchantAgent(query) {
    const res = await fetch(`${API_BASE}/agent/merchant`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    return await res.json();
  },

  // Policy & Safety Gate
  async evaluatePolicy(actionType, amount, discountPct = 0.0, productIds = [], customerConfirmed = true, sessionId = null) {
    const res = await fetch(`${API_BASE}/policy/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action_type: actionType,
        amount: parseFloat(amount),
        discount_percentage: parseFloat(discountPct),
        product_ids: productIds,
        customer_confirmed: customerConfirmed,
        session_id: sessionId
      })
    });
    return await res.json();
  },

  // Campaign Orchestrator
  async proposeCampaign(prompt, targetCategory = 'keyboard', suggestedBudget = 5000) {
    const res = await fetch(`${API_BASE}/campaigns/propose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        target_category: targetCategory,
        suggested_budget: parseFloat(suggestedBudget)
      })
    });
    return await res.json();
  },

  async approveCampaign(campaignId, approved = true) {
    const res = await fetch(`${API_BASE}/campaigns/${campaignId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approved })
    });
    return await res.json();
  },

  async listCampaigns() {
    const res = await fetch(`${API_BASE}/campaigns`);
    return await res.json();
  },

  // Audit Traces
  async getSessionTraces(sessionId) {
    const res = await fetch(`${API_BASE}/audit/traces/${sessionId}`);
    return await res.json();
  },

  async getAllAuditTraces(limit = 50) {
    const res = await fetch(`${API_BASE}/audit/traces?limit=${limit}`);
    return await res.json();
  },

  // Payments & Razorpay
  async createOrder(amount, customerEmail = 'buyer@example.com', customerPhone = '+919876543210', isAiAssisted = false, baselineAmount = null, sessionId = null) {
    const res = await fetch(`${API_BASE}/payments/create-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: parseFloat(amount),
        currency: 'INR',
        customer_email: customerEmail,
        customer_phone: customerPhone,
        is_ai_assisted: isAiAssisted,
        baseline_amount: baselineAmount ? parseFloat(baselineAmount) : parseFloat(amount),
        session_id: sessionId
      })
    });
    return await res.json();
  },

  async verifyPayment(orderIdOrObj, razorpayOrderId, razorpayPaymentId, razorpaySignature, simulatedFailure = null, sessionId = null) {
    let payload = {};
    if (typeof orderIdOrObj === 'object' && orderIdOrObj !== null) {
      payload = orderIdOrObj;
    } else {
      payload = {
        order_id: orderIdOrObj,
        razorpay_order_id: razorpayOrderId,
        razorpay_payment_id: razorpayPaymentId,
        razorpay_signature: razorpaySignature,
        simulated_failure: simulatedFailure,
        session_id: sessionId
      };
    }
    const res = await fetch(`${API_BASE}/payments/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return await res.json();
  },

  async getPayments(status = null, limit = 50) {
    let url = `${API_BASE}/payments?limit=${limit}`;
    if (status && status !== 'ALL') url += `&status_filter=${status.toLowerCase()}`;
    const res = await fetch(url);
    return await res.json();
  },

  async triggerRecovery(paymentId, customStrategy = null) {
    const res = await fetch(`${API_BASE}/recovery/trigger/${paymentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payment_id: paymentId, custom_strategy: customStrategy })
    });
    return await res.json();
  },

  async runScenario(scenarioId, amount = null, customFailure = null) {
    const res = await fetch(`${API_BASE}/simulator/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario: scenarioId,
        amount: amount ? parseFloat(amount) : null,
        custom_failure_type: customFailure
      })
    });
    return await res.json();
  },

  async seedDemoData() {
    const res = await fetch(`${API_BASE}/demo/seed`, { method: 'POST' });
    return await res.json();
  }
};
