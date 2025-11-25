const messageEl = document.getElementById('message');
const senderEl = document.getElementById('sender');
const filesEl = document.getElementById('files');
const analyzeBtn = document.getElementById('analyze');
const analyzeFilesBtn = document.getElementById('analyzeFiles');
const clearBtn = document.getElementById('clear');
const resultEl = document.getElementById('result');

const API_BASE = window.location.origin; // serves from same host: http://localhost:8000

function showStatus(msg, isError=false) {
  resultEl.innerHTML = `<div style="color:${isError? '#b31b1b':'#0b5fff'}">${msg}</div>`;
}

async function analyzeText(text, sender) {
  const res = await fetch(API_BASE + '/analyze', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({text, sender})
  });
  return res.json();
}

analyzeBtn.addEventListener('click', async () => {
  const text = messageEl.value.trim();
  const sender = senderEl.value.trim();
  if (!text) return showStatus('Paste a message or upload files first.', true);
  showStatus('Analyzing...');
  try {
    const j = await analyzeText(text, sender);
    if (!j.ok) throw new Error('analysis failed');
    renderResult(j.result);
  } catch (err) {
    showStatus('Error: ' + err.message, true);
  }
});

function renderResult(out) {
  const risk = out.risk_score;
  const level = out.risk_level;
  let color = '#2d7a2d';
  if (risk >= 0.7) color = '#b31b1b';
  else if (risk >= 0.4) color = '#b36f1b';

  resultEl.innerHTML = `
    <div><strong style="color:${color}">Risk: ${risk} (${level})</strong></div>
    <div style="margin-top:6px">${out.reasons.join('; ') || 'No obvious issues found.'}</div>
    <details style="margin-top:8px"><summary>Details</summary>
      <pre style="white-space:pre-wrap">${JSON.stringify(out.details, null, 2)}</pre>
    </details>
  `;
}

clearBtn.addEventListener('click', () => {
  messageEl.value = '';
  senderEl.value = '';
  filesEl.value = null;
  resultEl.innerHTML = '';
});

analyzeFilesBtn.addEventListener('click', async () => {
  const f = filesEl.files;
  if (!f || f.length === 0) return showStatus('Select one or more .eml/.txt files to analyze.', true);
  resultEl.innerHTML = '';
  for (let i=0;i<f.length;i++) {
    const file = f[i];
    const text = await file.text();
    showStatus('Analyzing ' + file.name + '...');
    try {
      const j = await analyzeText(text, senderEl.value.trim());
      const div = document.createElement('div');
      div.className = 'file-item';
      const verdict = (j.result.risk_level === 'high') ? 'SCAM' : (j.result.risk_level === 'medium' ? 'POTENTIAL' : 'OK');
      div.innerHTML = `<strong>${file.name} — ${verdict} (score ${j.result.risk_score})</strong><div style="margin-top:6px">${j.result.reasons.join('; ')}</div>`;
      resultEl.appendChild(div);
    } catch (err) {
      const errDiv = document.createElement('div');
      errDiv.className = 'file-item';
      errDiv.style.color = '#b31b1b';
      errDiv.textContent = file.name + ' — Error: ' + err.message;
      resultEl.appendChild(errDiv);
    }
  }
}
);
