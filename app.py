import os
import webbrowser
import threading
from flask import Flask, render_template, request

# Absolute path to ensure Flask finds 'STRUCTURE' correctly
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'STRUCTURE')

app = Flask(__name__, template_folder=template_dir)

@app.route("/")
def index():
    return render_template("questionnaire.html")

@app.route("/result", methods=["POST"])
def result():
    try:
        # Collecting all 15 inputs from your form
        data = {f"q{i}": int(request.form.get(f"q{i}", 5)) for i in range(1, 16)}
        
        # Categorical Scoring
        bio = (data['q1'] + data['q2'] + data['q3'] + data['q4'] + data['q5']) * 2
        cog = (data['q6'] + data['q7'] + data['q8'] + data['q9'] + data['q10']) * 2
        emo = (data['q11'] + data['q12'] + data['q13'] + data['q14'] + data['q15']) * 2
        score = int((bio + cog + emo) / 3)

        # Color-Coding & Informative Status
        if score < 40:
            status, color = "Critical Depletion", "#ef4444" # Red
            advice = "Immediate clinical rest required. Your physiological reserves are exhausted."
        elif score < 75:
            status, color = "Moderate Strain", "#f59e0b"   # Orange
            advice = "Your resilience is dipping. Prioritize recovery protocols to avoid burnout."
        else:
            status, color = "Optimal Resilience", "#10b981" # Green
            advice = "System stability is high. Maintain current wellness architecture."

        # Expert Guidance Focus
        lowest = min(bio, cog, emo)
        focus = "Physical" if lowest == bio else "Cognitive" if lowest == cog else "Emotional"

        return render_template("result.html", 
                               score=score, bio=bio, cog=cog, emo=emo, 
                               status=status, color=color, advice=advice,
                               focus=focus)
    except Exception as e:
        return f"Error: {e}. Please ensure all questions were answered."

if __name__ == "__main__":
    def open_browser():
        import time
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:5002")

    threading.Thread(target=open_browser, daemon=True).start()
    # Running on 5002 to force a fresh design load
    app.run(port=5002, debug=True, use_reloader=False)