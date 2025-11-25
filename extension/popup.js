const analyzeBtn = document.getElementById('analyze');
const reportBtn = document.getElementById('report');
const messageEl = document.getElementById('message');
const senderEl = document.getElementById('sender');
const resultEl = document.getElementById('result');
const thresholdEl = document.getElementById('threshold');
const thresholdLabel = document.getElementById('thresholdLabel');

thresholdEl.addEventListener('input', () => {
  thresholdLabel.textContent = thresholdEl.value;
  localStorage.setItem('ph_guard_threshold', thresholdEl.value);
});

// load saved threshold
const saved = localStorage.getItem('ph_guard_threshold');
if (saved) {
  thresholdEl.value = saved;
  thresholdLabel.textContent = saved;
}

async function analyze() {
  const text = messageEl.value.trim();
  const sender = senderEl.value.trim();
  if (!text) {
    resultEl.textContent = 'Please paste a message to analyze.';
    return;
  }

  resultEl.textContent = 'Analyzing...';
  try {
    const res = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, sender }),
    });
    const j = await res.json();
    if (!j.ok) throw new Error('analysis failed');
    const out = j.result;
    showResult(out);
  } catch (err) {
    resultEl.textContent = 'Error: ' + err.message + '\nEnsure the backend server is running at http://localhost:8000';
  }
}

function showResult(out) {
  const threshold = parseFloat(thresholdEl.value || '0.5');
  const risk = out.risk_score;
  const level = out.risk_level;
  let color = '#2d7a2d';
  if (risk >= 0.7) color = '#b31b1b';
  else if (risk >= 0.4) color = '#b36f1b';

  resultEl.innerHTML = `
    <div><strong style="color:${color}">Risk: ${risk} (${level})</strong></div>
    <div>${out.reasons.join('; ') || 'No obvious issues found.'}</div>
    <details style="margin-top:8px"><summary>Details</summary>
      <pre style="white-space:pre-wrap">${JSON.stringify(out.details, null, 2)}</pre>
    </details>
  `;

  // visual cue if above threshold
  if (risk >= threshold) {
    resultEl.style.border = '2px solid ' + color;
  } else {
    resultEl.style.border = '1px solid #e6e6e6';
  }
}

analyzeBtn.addEventListener('click', analyze);

reportBtn.addEventListener('click', async () => {
  const text = messageEl.value.trim();
  const sender = senderEl.value.trim();
  if (!text) return alert('Paste the message before reporting.');
  try {
    const res = await fetch('http://localhost:8000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, sender }),
    });
    const j = await res.json();
    if (j.ok) alert('Report submitted (prototype).');
    else alert('Report failed');
  } catch (err) {
    alert('Error sending report. Is the backend running?');
  }
});
