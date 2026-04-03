import os
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify

# Absolute path to ensure Flask finds folders correctly
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'STRUCTURE')
static_dir   = os.path.join(base_dir, 'DESIGN')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    name = request.form.get("name", "Student") if request.method == "POST" else "Student"
    return render_template("dashboard.html", name=name)

@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")

@app.route("/assistant")
def assistant():
    return render_template("assistant.html")

@app.route("/result", methods=["POST"])
def result():
    try:
        data = {f"q{i}": int(request.form.get(f"q{i}", 5)) for i in range(1, 16)}

        bio   = (data['q1'] + data['q2'] + data['q3'] + data['q4'] + data['q5']) * 2
        cog   = (data['q6'] + data['q7'] + data['q8'] + data['q9'] + data['q10']) * 2
        emo   = (data['q11'] + data['q12'] + data['q13'] + data['q14'] + data['q15']) * 2
        score = int((bio + cog + emo) / 3)

        if score < 40:
            status, color = "Critical Depletion", "#ef4444"
            advice = "Immediate clinical rest required. Your physiological reserves are exhausted. Please reach out to a counselor or mental health professional as soon as possible."
        elif score < 75:
            status, color = "Moderate Strain", "#f59e0b"
            advice = "Your resilience is dipping. Prioritize sleep, reduce screen time, and consider speaking to a peer counselor. Avoid taking on new commitments right now."
        else:
            status, color = "Optimal Resilience", "#0ee6b7"
            advice = "System stability is high. Maintain your current wellness habits, stay consistent with sleep and exercise, and keep checking in with yourself regularly."

        lowest = min(bio, cog, emo)
        focus  = "Physical" if lowest == bio else "Cognitive" if lowest == cog else "Emotional"

        return render_template("result.html",
                               score=score, bio=bio, cog=cog, emo=emo,
                               status=status, color=color, advice=advice,
                               focus=focus)
    except Exception as e:
        return f"Error: {e}"

@app.route("/chat", methods=["POST"])
def chat():
    """Simple AI chat endpoint — replace with real model if needed."""
    msg = request.json.get("message", "").lower()

    responses = {
        "stress":   "It sounds like you're under a lot of pressure. Try the 4-7-8 breathing technique — inhale for 4s, hold for 7s, exhale for 8s. Would you like more coping strategies?",
        "anxious":  "Anxiety can feel overwhelming. Grounding yourself with the 5-4-3-2-1 technique often helps — name 5 things you can see right now.",
        "sad":      "I'm sorry you're feeling this way. It's okay to not be okay. Would talking about what's on your mind help? I'm here.",
        "sleep":    "Poor sleep amplifies everything. Try keeping your phone away 30 minutes before bed and keeping a consistent sleep schedule.",
        "tired":    "Fatigue can be both physical and emotional. Have you had water and a proper meal today? Small things matter.",
        "lonely":   "Loneliness is really tough, especially as a student. Even sending one message to a friend today can shift things a bit.",
        "angry":    "It's valid to feel angry. Try to pause before reacting — even 60 seconds of deep breathing creates space between the feeling and the response.",
    }

    reply = "I hear you. It takes courage to talk about how you're feeling. Can you tell me a little more about what's been going on?"
    for keyword, response in responses.items():
        if keyword in msg:
            reply = response
            break

    return jsonify({"reply": reply})

if __name__ == "__main__":
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5002")

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(port=5002, debug=True, use_reloader=False)
