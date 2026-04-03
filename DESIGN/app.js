// ── MOOD CHART ──────────────────────────────
function initMoodChart() {
  const canvas = document.getElementById('moodChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const brand = '#0ee6b7';
  const brandDim = 'rgba(14,230,183,0.12)';

  const gradient = ctx.createLinearGradient(0, 0, 0, 220);
  gradient.addColorStop(0, 'rgba(14,230,183,0.25)');
  gradient.addColorStop(1, 'rgba(14,230,183,0)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Mood Score',
        data: [62, 75, 58, 80, 70, 88, 74],
        borderColor: brand,
        borderWidth: 2.5,
        pointBackgroundColor: brand,
        pointBorderColor: '#060b14',
        pointBorderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        fill: true,
        backgroundColor: gradient,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0c1422',
          borderColor: 'rgba(14,230,183,0.3)',
          borderWidth: 1,
          titleColor: '#0ee6b7',
          bodyColor: '#e8f0fe',
          padding: 12,
          callbacks: {
            label: ctx => ` Score: ${ctx.parsed.y}/100`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          border: { display: false },
          ticks: { color: '#6b7fa3', font: { family: 'DM Sans', size: 12 } }
        },
        y: {
          min: 0, max: 100,
          grid: { color: 'rgba(255,255,255,0.04)' },
          border: { display: false },
          ticks: {
            color: '#6b7fa3',
            font: { family: 'DM Sans', size: 12 },
            callback: v => v + '%'
          }
        }
      }
    }
  });
}

// ── AI CHAT ──────────────────────────────────
const chatBox   = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');

function appendMsg(text, type) {
  if (!chatBox) return;
  const div = document.createElement('div');
  div.classList.add('msg', type === 'user' ? 'msg-user' : 'msg-ai');

  if (type === 'ai') {
    div.innerHTML = `<strong>MindGuard AI</strong>${text}`;
  } else {
    div.textContent = text;
  }

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
  if (!chatBox) return;
  const div = document.createElement('div');
  div.classList.add('msg', 'msg-ai');
  div.id = 'typing-indicator';
  div.innerHTML = `<strong>MindGuard AI</strong><span style="opacity:0.5;letter-spacing:3px">●●●</span>`;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

async function sendMessage() {
  const text = userInput?.value?.trim();
  if (!text) return;

  appendMsg(text, 'user');
  userInput.value = '';
  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    removeTyping();
    appendMsg(data.reply || 'I\'m here. Take your time.', 'ai');
  } catch {
    removeTyping();
    appendMsg('I\'m here for you. Could you tell me more about how you\'re feeling?', 'ai');
  }
}

// Allow Enter to send
document.addEventListener('DOMContentLoaded', () => {
  initMoodChart();

  // Greet user on dashboard load
  setTimeout(() => {
    const name = document.querySelector('[data-username]')?.dataset?.username;
    if (chatBox) {
      appendMsg(
        `Hello${name ? ', ' + name : ''}! 👋 I\'m your MindGuard AI support assistant. How are you feeling today?`,
        'ai'
      );
    }
  }, 600);

  if (userInput) {
    userInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Animate stat cards in
  document.querySelectorAll('.stat-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
      card.style.transition = 'all 0.5s cubic-bezier(0.4,0,0.2,1)';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 100 + i * 80);
  });

  // Animate metric bars on result page
  document.querySelectorAll('.metric-fill').forEach(bar => {
    const target = bar.dataset.width;
    if (target) {
      bar.style.width = '0%';
      setTimeout(() => { bar.style.width = target + '%'; }, 400);
    }
  });

  // Live date in dashboard
  const dateEl = document.getElementById('dashDate');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });
  }
});
