/**
 * RAZORFLOW X - Charts & Visual Telemetry Controller
 * Resilient Multi-Backend Chart Engine (Chart.js + Native Canvas Fallback)
 */
window.Charts = {
  hourlyChart: null,
  riskChart: null,
  experimentChart: null,
  bankLatencyChart: null,

  initHourlyChart(ctx, data) {
    if (!ctx) return;
    const items = data || [
      { time: '00:00', transactions: 2, recovered: 0 },
      { time: '04:00', transactions: 8, recovered: 2 },
      { time: '08:00', transactions: 24, recovered: 3 },
      { time: '12:00', transactions: 16, recovered: 2 },
      { time: '16:00', transactions: 34, recovered: 13 },
      { time: '20:00', transactions: 25, recovered: 10 },
      { time: '23:00', transactions: 24, recovered: 9 }
    ];

    if (typeof Chart !== 'undefined') {
      try {
        if (this.hourlyChart) this.hourlyChart.destroy();
        this.hourlyChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: items.map(d => d.time),
            datasets: [
              {
                label: 'Total Processed Orders',
                data: items.map(d => d.transactions),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                fill: true,
                tension: 0.35,
                borderWidth: 2.5
              },
              {
                label: 'Autonomous Self-Healing Salvages',
                data: items.map(d => d.recovered),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                fill: true,
                tension: 0.35,
                borderWidth: 2
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } }
            },
            scales: {
              x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
              y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' }, beginAtZero: true }
            }
          }
        });
        return;
      } catch (err) {
        console.warn('Chart.js error, falling back to Canvas:', err);
      }
    }

    // Native Canvas Line Chart Fallback
    const cvs = ctx.canvas;
    const w = cvs.width = cvs.clientWidth || 340;
    const h = cvs.height = cvs.clientHeight || 200;
    ctx.clearRect(0, 0, w, h);

    // Draw Grid
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    for (let y = 30; y < h - 30; y += 35) {
      ctx.beginPath();
      ctx.moveTo(35, y);
      ctx.lineTo(w - 15, y);
      ctx.stroke();
    }

    const txs = items.map(d => d.transactions);
    const maxVal = Math.max(...txs, 35);
    const stepX = (w - 60) / (items.length - 1);

    // Line 1: Orders (Indigo)
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 3;
    ctx.beginPath();
    items.forEach((d, i) => {
      const x = 40 + i * stepX;
      const y = h - 35 - (d.transactions / maxVal) * (h - 70);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Line 2: Recovered (Green)
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    items.forEach((d, i) => {
      const x = 40 + i * stepX;
      const y = h - 35 - (d.recovered / maxVal) * (h - 70);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Labels
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px Inter, sans-serif';
    items.forEach((d, i) => {
      const x = 40 + i * stepX;
      ctx.fillText(d.time, x - 12, h - 10);
    });
  },

  initRiskChart(ctx, riskBreakdown) {
    if (!ctx) return;
    const low = (riskBreakdown && riskBreakdown.LOW) || 420;
    const med = (riskBreakdown && riskBreakdown.MEDIUM) || 65;
    const high = (riskBreakdown && riskBreakdown.HIGH) || 15;

    if (typeof Chart !== 'undefined') {
      try {
        if (this.riskChart) this.riskChart.destroy();
        this.riskChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Low Risk (Fast-Track)', 'Medium Risk', 'High Risk (Flagged)'],
            datasets: [{
              data: [low, med, high],
              backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
              borderColor: '#0f172a',
              borderWidth: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } }
            }
          }
        });
        return;
      } catch (err) {
        console.warn('Chart.js error on risk chart:', err);
      }
    }

    // Native Canvas Donut Fallback
    const cvs = ctx.canvas;
    const w = cvs.width = cvs.clientWidth || 280;
    const h = cvs.height = cvs.clientHeight || 200;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2 - 10;
    const outerR = Math.min(cx, cy) - 15;
    const innerR = outerR * 0.6;
    const total = low + med + high;

    const slices = [
      { val: low, color: '#10b981' },
      { val: med, color: '#f59e0b' },
      { val: high, color: '#f43f5e' }
    ];

    let startAngle = -Math.PI / 2;
    slices.forEach(s => {
      const sliceAngle = (s.val / total) * (Math.PI * 2);
      ctx.beginPath();
      ctx.arc(cx, cy, outerR, startAngle, startAngle + sliceAngle);
      ctx.arc(cx, cy, innerR, startAngle + sliceAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = s.color;
      ctx.fill();
      startAngle += sliceAngle;
    });

    // Donut Center Text
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 13px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('96.2% LOW', cx, cy + 4);
  },

  initBankLatencyChart(ctx, data) {
    if (!ctx) return;
    const banks = data ? data.map(d => d.bank) : ['HDFC', 'ICICI', 'SBI', 'Axis', 'Kotak', 'Yes Bank'];
    const latencies = data ? data.map(d => d.latency_ms) : [140, 180, 890, 220, 160, 1450];
    const bgColors = latencies.map(l => l > 1000 ? '#f43f5e' : (l > 500 ? '#f59e0b' : '#10b981'));

    if (typeof Chart !== 'undefined') {
      try {
        if (this.bankLatencyChart) this.bankLatencyChart.destroy();
        this.bankLatencyChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: banks,
            datasets: [{
              label: 'Gateway Latency (ms)',
              data: latencies,
              backgroundColor: bgColors,
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: '#94a3b8', font: { family: 'Inter', size: 10 } } }
            },
            scales: {
              x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8', font: { size: 10 } } },
              y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' }, beginAtZero: true }
            }
          }
        });
        return;
      } catch (err) {
        console.warn('Chart.js error on latency chart:', err);
      }
    }

    // Native Canvas Bar Chart Fallback
    const cvs = ctx.canvas;
    const w = cvs.width = cvs.clientWidth || 320;
    const h = cvs.height = cvs.clientHeight || 200;
    ctx.clearRect(0, 0, w, h);

    const maxL = 1600;
    const barWidth = (w - 70) / banks.length - 8;

    banks.forEach((b, i) => {
      const lat = latencies[i];
      const barH = (lat / maxL) * (h - 60);
      const x = 35 + i * (barWidth + 8);
      const y = h - 30 - barH;

      ctx.fillStyle = bgColors[i];
      ctx.fillRect(x, y, barWidth, barH);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(b.substring(0, 5), x + barWidth / 2, h - 12);
    });
  },

  initExperimentChart(ctx, experimentData) {
    if (!ctx) return;
    const c = (experimentData && experimentData.control_metrics) || { conversion_rate: 8.2, aov: 1420, revenue_per_session: 116 };
    const t = (experimentData && experimentData.treatment_metrics) || { conversion_rate: 11.7, aov: 1691, revenue_per_session: 198 };

    if (typeof Chart !== 'undefined') {
      try {
        if (this.experimentChart) this.experimentChart.destroy();
        this.experimentChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Conversion Rate (%)', 'Avg Order Value (₹/100)', 'Revenue/Session (₹)'],
            datasets: [
              {
                label: 'Control (Standard Store)',
                data: [c.conversion_rate, c.aov / 100.0, c.revenue_per_session],
                backgroundColor: 'rgba(148, 163, 184, 0.5)',
                borderRadius: 6
              },
              {
                label: 'Treatment (RAZORFLOW X)',
                data: [t.conversion_rate, t.aov / 100.0, t.revenue_per_session],
                backgroundColor: 'rgba(6, 182, 212, 0.8)',
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'top', labels: { color: '#94a3b8', font: { family: 'Inter', size: 10 } } }
            },
            scales: {
              x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
              y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' }, beginAtZero: true }
            }
          }
        });
        return;
      } catch (err) {
        console.warn('Chart.js error on experiment chart:', err);
      }
    }

    // Native Canvas Bar Fallback
    const cvs = ctx.canvas;
    const w = cvs.width = cvs.clientWidth || 500;
    const h = cvs.height = cvs.clientHeight || 220;
    ctx.clearRect(0, 0, w, h);

    const metrics = [
      { name: 'CR (%)', c: c.conversion_rate, t: t.conversion_rate, max: 20 },
      { name: 'AOV (₹/100)', c: c.aov / 100, t: t.aov / 100, max: 25 },
      { name: 'RPS (₹)', c: c.revenue_per_session, t: t.revenue_per_session, max: 250 }
    ];

    const groupW = (w - 60) / 3;
    metrics.forEach((m, i) => {
      const gx = 40 + i * groupW;
      const cHeight = (m.c / m.max) * (h - 70);
      const tHeight = (m.t / m.max) * (h - 70);

      // Control bar
      ctx.fillStyle = 'rgba(148, 163, 184, 0.5)';
      ctx.fillRect(gx, h - 35 - cHeight, groupW * 0.35, cHeight);

      // Treatment bar
      ctx.fillStyle = 'rgba(6, 182, 212, 0.85)';
      ctx.fillRect(gx + groupW * 0.4, h - 35 - tHeight, groupW * 0.35, tHeight);

      // Label
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(m.name, gx + groupW * 0.35, h - 12);
    });
  }
};
