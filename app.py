import os
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify, session

# Absolute path to ensure Flask finds folders correctly
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'STRUCTURE')
static_dir   = os.path.join(base_dir, 'DESIGN')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = "mindguard_secret_2026"

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        session["name"] = request.form.get("name", "Student")
        # Reset streak only on first login if not set
        if "streak" not in session:
            session["streak"] = 0
        if "sessions_done" not in session:
            session["sessions_done"] = 0

    name = session.get("name", "Student")

    # Get dynamic data from session
    resilience  = session.get("resilience_score", None)
    streak      = session.get("streak", 0)
    sessions    = session.get("sessions_done", 0)
    risk        = session.get("risk_level", None)
    mood_today  = session.get("mood_today", None)

    return render_template("dashboard.html",
                           name=name,
                           resilience=resilience,
                           streak=streak,
                           sessions=sessions,
                           risk=risk,
                           mood_today=mood_today)

@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")

@app.route("/assistant")
def assistant():
    return render_template("assistant.html")

@app.route("/mood")
def mood():
    return render_template("mood.html")

@app.route("/save_mood", methods=["POST"])
def save_mood():
    data = request.json
    session["mood_today"] = {
        "emoji": data.get("emoji"),
        "label": data.get("label"),
        "score": data.get("score"),
        "color": data.get("color")
    }
    session["streak"] = session.get("streak", 0) + 1
    return jsonify({"status": "saved"})

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

        # Save to session
        session["resilience_score"] = score
        session["sessions_done"]    = session.get("sessions_done", 0) + 1
        session["streak"]           = session.get("streak", 0) + 1
        session["risk_level"]       = "High" if score < 40 else "Moderate" if score < 75 else "Low"

        return render_template("result.html",
                               score=score, bio=bio, cog=cog, emo=emo,
                               status=status, color=color, advice=advice,
                               focus=focus)
    except Exception as e:
        return f"Error: {e}"

@app.route("/chat", methods=["POST"])
def chat():
    import random
    msg = request.json.get("message", "").lower()

    responses = {
        # Stress
        "stress": [
            "It sounds like you're carrying a lot right now. Try the 4-7-8 breathing technique — inhale for 4s, hold for 7s, exhale for 8s. It genuinely helps calm your nervous system.",
            "Stress is your mind's way of saying it needs a break. Even a 5-minute walk outside can reset your headspace. You've got this. 💙",
            "When stress builds up, try writing down everything on your mind — just getting it out of your head onto paper reduces the mental load a lot."
        ],
        # Anxiety
        "anxious": [
            "Anxiety can feel really overwhelming. Try the 5-4-3-2-1 grounding technique — name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. It brings you back to the present.",
            "When anxiety spikes, your breath is your anchor. Try box breathing — inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 4 times.",
            "It's okay to feel anxious. It means you care. But don't let the 'what ifs' take over — focus only on what you can control right now."
        ],
        "anxiety": [
            "Anxiety is tough but manageable. Start small — identify one thing causing the anxiety and ask yourself: is this in my control? If yes, act. If no, let it go.",
            "Deep breathing activates your parasympathetic nervous system and lowers anxiety fast. Try it right now — slow breath in, slow breath out.",
        ],
        # Sad / Crying
        "sad": [
            "I'm really sorry you're feeling this way. It's completely okay to not be okay sometimes. You don't have to explain yourself — just know you're not alone. 💙",
            "Sadness is a valid emotion. Give yourself permission to feel it without guilt. Is there something specific that triggered this, or just a general low feeling?",
            "On hard days, even small things help — a warm drink, your favourite song, or just lying down for a bit. Be gentle with yourself today."
        ],
        "cry": [
            "Sometimes crying is exactly what you need — it's your body releasing pressure. Let it out. You'll feel lighter after.",
            "It's okay to cry. It doesn't mean you're weak — it means you're human. I'm here with you. 💙"
        ],
        "crying": [
            "Let it out. Crying is healing. When you're ready, take a deep breath and know that this feeling will pass.",
        ],
        # Sleep
        "sleep": [
            "Poor sleep makes everything harder — mood, focus, energy. Try keeping your phone away 30 mins before bed and sleeping at the same time every night. Your brain loves routine.",
            "If your mind races at night, try writing a quick brain dump before bed — just dump all your thoughts on paper so your brain can finally rest.",
            "No screens 30 minutes before bed, a cool dark room, and consistent sleep timing — these three things alone can transform your sleep quality."
        ],
        "insomnia": [
            "Insomnia is exhausting, both mentally and physically. Try progressive muscle relaxation — tense and release each muscle group from toes to head. It signals your body to sleep.",
            "If you can't sleep after 20 minutes, get up and do something calm like reading until you feel sleepy again. Lying in bed awake trains your brain to associate bed with wakefulness."
        ],
        # Tired / Exhausted
        "tired": [
            "Fatigue can be physical or emotional — both are valid. Have you had water and a proper meal today? Small things matter more than we think.",
            "Sometimes tiredness is your body asking for rest, not just sleep. A 10-minute break with no screens can help more than you'd expect.",
            "Chronic tiredness often comes from doing too much for too long. It's okay to slow down. Rest is productive too."
        ],
        "exhausted": [
            "You sound really drained. Please be kind to yourself today — you don't have to do everything at once. One thing at a time.",
            "Emotional exhaustion is real and it hits harder than physical tiredness. Take a break if you can — even 15 minutes of doing nothing is recovery."
        ],
        # Lonely
        "lonely": [
            "Loneliness as a student is more common than anyone admits. Even sending one message to a friend today can shift how you feel. You matter to people, even when it doesn't feel like it.",
            "Feeling lonely doesn't mean you are alone. Sometimes it just means you need connection. Is there one person you could reach out to today — even just a meme or a voice note?",
        ],
        "alone": [
            "Feeling alone is one of the hardest emotions. But you reached out here, which tells me a part of you is looking for connection. That's brave. 💙",
        ],
        # Angry
        "angry": [
            "Anger is valid — it usually means something important to you was crossed. But before you react, give yourself 60 seconds. Breathe. Then decide.",
            "When you're really angry, physical movement helps — even just a brisk walk or punching a pillow. Get that energy out of your body first.",
        ],
        "frustrated": [
            "Frustration usually builds up when we feel stuck or unheard. What's the one thing frustrating you the most right now?",
            "Take a step back. Sometimes the best thing you can do when frustrated is walk away for 10 minutes and come back with fresh eyes."
        ],
        # Overwhelmed
        "overwhelmed": [
            "When everything feels too much, break it down to just ONE thing. What is the single most important thing you need to do right now? Start only there.",
            "Overwhelm is your brain processing too much at once. Write everything down, then pick just 3 things for today. The rest can wait.",
            "It's okay to feel overwhelmed. You're probably doing a lot. Take a breath, drink some water, and remember — you don't have to do it all today."
        ],
        # Motivation / Focus
        "motivat": [
            "Motivation comes and goes — discipline is what keeps you going. Start with just 2 minutes on the task. Often starting is the hardest part.",
            "On low motivation days, reduce the task size. Instead of 'study for 3 hours', make it 'open the book for 5 minutes'. Small wins build momentum."
        ],
        "focus": [
            "Trouble focusing? Try the Pomodoro technique — 25 minutes of focused work, 5 minute break. Repeat. Your brain works better in short bursts.",
            "Remove one distraction at a time. Put your phone in another room, close extra tabs, and give yourself just one task to focus on."
        ],
        "concentrate": [
            "Concentration dips when your brain is tired or overstimulated. A 5-minute walk, some water, and a clear desk can help more than you'd think.",
        ],
        # Exam / Studies
        "exam": [
            "Exam stress is real! Break your syllabus into small daily chunks. And remember — one bad exam doesn't define you or your future.",
            "Before an exam, avoid cramming the night before. Light revision, good sleep, and a proper breakfast will serve you better than an all-nighter.",
        ],
        "study": [
            "Studying feels hard when you're already drained. Try active recall instead of re-reading — test yourself on what you know. It's faster and sticks better.",
            "Study in a clean, quiet space if possible. Even 45 focused minutes beats 3 hours of distracted studying."
        ],
        "marks": [
            "Marks are important but they don't measure your worth. Focus on understanding the concepts — marks will follow.",
            "One bad result is just data, not a verdict. What can you do differently next time? That's all that matters."
        ],
        # Pressure
        "pressure": [
            "Academic and social pressure is crushing for students. Please remember — you are more than your grades, your productivity, or what others think of you.",
            "When pressure builds up, talk to someone you trust. Keeping it bottled up makes it heavier. You don't have to carry it alone."
        ],
        # Happy / Good
        "happy": [
            "That's wonderful to hear! 😊 What's making you feel good today? Hold onto that feeling.",
            "Love that energy! Keep doing whatever is working for you right now. 🌟"
        ],
        "good": [
            "Really glad to hear you're doing well! Remember this feeling on harder days — it always comes back around. 😊",
        ],
        "great": [
            "Amazing! 🎉 You deserve to feel great. Keep that energy going!"
        ],
        # Help
        "help": [
            "I'm here for you. You can talk to me about stress, anxiety, sleep, focus, relationships — anything that's on your mind. What's going on?",
            "Of course. Tell me what's bothering you and we'll figure it out together. 💙"
        ],
        # Greetings
        "hello": [
            "Hey! 👋 How are you feeling today? I'm here to listen and support you.",
            "Hi there! What's on your mind today?"
        ],
        "hi": [
            "Hey! 😊 How are you doing today?",
            "Hi! I'm your MindGuard support assistant. How are you feeling right now?"
        ],
        "how are you": [
            "I'm here and ready to support you! More importantly — how are YOU feeling today? 😊"
        ],
        # Panic / Crisis
        "panic": [
            "If you're having a panic attack — you are safe. It will pass. Focus on your breathing: slow inhale through nose, slow exhale through mouth. You are not in danger.",
            "Panic attacks are terrifying but not dangerous. Ground yourself: press your feet flat on the floor, feel the chair under you, name 3 things you can see. You're here. You're okay."
        ],
        "depressed": [
            "I hear you, and I want you to know — what you're feeling is real and valid. Depression is not weakness. Please consider speaking to a counselor or trusted adult. You deserve proper support. 💙",
            "Depression can make everything feel heavy and pointless. Please don't face this alone — talk to someone you trust or reach out to a mental health helpline. iCall: 9152987821"
        ],
        "depression": [
            "Thank you for sharing that. Depression is serious and you deserve real support. Please reach out to iCall at 9152987821 or speak to your college counselor. You are not alone in this. 💙"
        ],
        "suicide": [
            "Please reach out for help right now. You matter more than you know. iCall helpline: 9152987821. Vandrevala Foundation: 1860-2662-345 (24/7). You don't have to face this alone. 💙"
        ],
        "die": [
            "I'm concerned about you. Please talk to someone you trust right now, or call iCall: 9152987821. You are valued and your life matters. 💙"
        ],
    }

    reply = "I hear you. It takes courage to reach out. Can you tell me a little more about how you're feeling right now? I'm here to listen. 💙"

    for keyword, response_list in responses.items():
        if keyword in msg:
            reply = random.choice(response_list) if isinstance(response_list, list) else response_list
            break

    return jsonify({"reply": reply})

if __name__ == "__main__":
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5002")

    threading.Thread(target=open_browser, daemon=True).start()
    app.run(port=5002, debug=True, use_reloader=False)
