/**
 * RAZORFLOW X - Payment Reliability Simulator Module
 */
const Simulator = {
  currentScenario: 1,

  selectScenario(id) {
    this.currentScenario = id;
    document.querySelectorAll('.scenario-card').forEach(el => el.classList.remove('active-scenario'));
    const target = document.getElementById(`scenario-card-${id}`);
    if (target) target.classList.add('active-scenario');

    const configArea = document.getElementById('sim-custom-config');
    if (id === 4) {
      configArea.style.display = 'block';
    } else {
      configArea.style.display = 'none';
    }
  },

  async executeCurrentScenario() {
    const btn = document.getElementById('btn-run-simulation');
    btn.disabled = true;
    btn.innerHTML = `<span class="status-dot"></span> Processing Scenario ${this.currentScenario}...`;

    const vizContainer = document.getElementById('sim-timeline-view');
    vizContainer.innerHTML = `<div style="text-align: center; color: var(--accent-cyan); padding: 2rem;">Processing transaction through Adaptive Risk Pipeline & Gateway...</div>`;

    let customAmount = null;
    let customFailure = null;

    if (this.currentScenario === 4) {
      customAmount = document.getElementById('custom-sim-amount').value || 1500;
      customFailure = document.getElementById('custom-sim-failure').value || 'TIMEOUT';
    }

    try {
      const res = await API.runScenario(this.currentScenario, customAmount, customFailure);
      this.renderSimulationResult(res);
      // Trigger global metrics refresh
      if (window.App) window.App.refreshData();
    } catch (err) {
      vizContainer.innerHTML = `<div style="color: var(--accent-rose); padding: 1rem;">Execution Error: ${err.message}</div>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = `Execute Scenario ${this.currentScenario}`;
    }
  },

  renderSimulationResult(res) {
    const vizContainer = document.getElementById('sim-timeline-view');
    
    if (res.scenario === 4 && res.ai_response) {
      const ai = res.ai_response;
      vizContainer.innerHTML = `
        <div class="glass-panel" style="padding: 1.5rem; border-color: var(--accent-cyan);">
          <div style="font-size: 1.1rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 0.5rem;">Reliability Diagnostics & Executive Report</div>
          <div style="font-size: 0.95rem; line-height: 1.6; margin-bottom: 1rem;">${ai.answer.replace(/\n/g, '<br>')}</div>
          <div style="font-weight: 600; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.35rem;">Dominant Loss Contributors:</div>
          <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
            ${ai.contributors.map(c => `<li>${c}</li>`).join('')}
          </ul>
          <div style="font-weight: 600; font-size: 0.85rem; color: var(--accent-emerald); margin-bottom: 0.35rem;">Autonomous Remediation Plan:</div>
          <ul style="padding-left: 1.25rem; font-size: 0.85rem; color: var(--accent-emerald);">
            ${ai.recommended_actions.map(a => `<li>${a}</li>`).join('')}
          </ul>
        </div>
      `;
      return;
    }

    let riskBadgeClass = 'badge-low';
    if (res.risk_level === 'HIGH') riskBadgeClass = 'badge-high';
    else if (res.risk_level === 'MEDIUM') riskBadgeClass = 'badge-med';

    let statusPillClass = 'badge-success';
    if (res.final_status === 'RECOVERED' || res.status === 'SUCCESS') statusPillClass = 'badge-success';
    else if (res.status && res.status.includes('BLOCKED')) statusPillClass = 'badge-failed';
    else statusPillClass = 'badge-recovered';

    let html = `
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 1rem;">
        <div>
          <div style="font-size: 1.1rem; font-weight: 800;">${res.title}</div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">Transaction ID: <code>${res.payment_id}</code> | Amount: <strong>₹${res.amount ? res.amount.toLocaleString() : '0'}</strong></div>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <span class="badge ${riskBadgeClass}">Risk: ${res.risk_score}/100 (${res.risk_level})</span>
          <span class="badge ${statusPillClass}">${res.recovery_status || res.status}</span>
        </div>
      </div>

      <div style="font-size: 0.9rem; margin-bottom: 1rem; color: ${res.status && res.status.includes('BLOCKED') ? 'var(--accent-rose)' : 'var(--accent-emerald)'}; font-weight: 600;">
        ${res.message}
      </div>

      <div style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Execution Telemetry & Recovery Timeline:</div>
      <div class="timeline-container">
    `;

    if (res.timeline && res.timeline.length) {
      res.timeline.forEach((item, idx) => {
        const itemStatus = item.status || 'SUCCESS';
        html += `
          <div class="timeline-item status-${itemStatus}">
            <div style="font-size: 0.9rem; font-weight: 800;">
              [${itemStatus}]
            </div>
            <div style="flex: 1;">
              <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 0.85rem;">
                <span>${item.step || `Attempt #${item.attempt_number} - ${item.strategy}`}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted);">${item.delay_ms ? `+${item.delay_ms}ms backoff` : ''}</span>
              </div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                ${item.details || item.status}
              </div>
            </div>
          </div>
        `;
      });
    }

    html += `</div>`;
    vizContainer.innerHTML = html;
  }
};
