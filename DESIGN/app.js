// ===== CHART =====
const ctx = document.getElementById('chart');

if (ctx) {
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
      datasets: [{
        data: [6,7,5,8,7,9,8],
        borderColor: '#2563eb',
        tension: 0.4
      }]
    },
    options: {
      plugins: { legend: { display: false } }
    }
  });
}


// ===== CHAT STATE =====
let lastTopic = "";

// ===== SEND MESSAGE =====
function sendMessage() {
  const input = document.getElementById("userInput");
  const chatBox = document.getElementById("chatBox");

  let text = input.value.trim();
  if (!text) return;

  chatBox.innerHTML += `<div class="user">${text}</div>`;

  const reply = generateResponse(text);

  chatBox.innerHTML += `<div class="bot">Typing...</div>`;

  setTimeout(() => {
    chatBox.innerHTML = chatBox.innerHTML.replace("Typing...", reply);
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 700);

  input.value = "";
}


// ===== SMART RESPONSE ENGINE =====
function generateResponse(text) {
  text = text.toLowerCase();

  // GREETING
  if (text.includes("hi") || text.includes("hello") || text.includes("hey")) {
    lastTopic = "intro";
    return "Hello. I'm your mental health assistant. How are you feeling today?";
  }

  // GOOD MOOD
  if (text.includes("good") || text.includes("fine") || text.includes("okay")) {
    lastTopic = "positive";
    return "That's good to hear. Maintaining balance in sleep, work, and relaxation is important.";
  }

  // STRESS
  if (text.includes("stress") || text.includes("pressure") || text.includes("overwork")) {
    lastTopic = "stress";
    return "It seems you're experiencing stress. Try dividing your work into smaller tasks and take short breaks regularly.";
  }

  // SAD
  if (text.includes("sad") || text.includes("low") || text.includes("depressed")) {
    lastTopic = "sad";
    return "I'm sorry you're feeling this way. Talking to someone or writing your thoughts down can help process emotions.";
  }

  // ANXIETY
  if (text.includes("anxiety") || text.includes("anxious") || text.includes("panic")) {
    lastTopic = "anxiety";
    return "Anxiety can be overwhelming. Try slow breathing: inhale for 4 seconds, hold for 4, exhale for 4.";
  }

  // LONELY
  if (text.includes("alone") || text.includes("lonely")) {
    lastTopic = "lonely";
    return "Feeling lonely can be difficult. Even small interactions or reaching out to one person can help.";
  }

  // TIRED
  if (text.includes("tired") || text.includes("exhausted")) {
    lastTopic = "tired";
    return "It sounds like you need rest. Proper sleep and short breaks can significantly improve your energy.";
  }

  // FOLLOW-UP BASED ON LAST TOPIC
  if (lastTopic === "stress") {
    return "Would you like some quick techniques to reduce stress right now?";
  }

  if (lastTopic === "sad") {
    return "Would you like to talk about what's making you feel this way?";
  }

  if (lastTopic === "anxiety") {
    return "Are you experiencing this frequently or occasionally?";
  }

  // DEFAULT (CONTROLLED — NOT CHILDISH)
  return "I understand. Could you describe your situation a bit more so I can assist you better?";
}