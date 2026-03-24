from flask import Flask, render_template, request
import webbrowser
import threading

app = Flask(__name__, template_folder='STRUCTURE', static_folder='DESIGN')


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():
    name = request.form["name"]
    return render_template("dashboard.html", name=name)


@app.route("/questionnaire")
def questionnaire():
    return render_template("questionnaire.html")


@app.route("/result", methods=["POST"])
def result():
    stress = int(request.form["stress"])
    sleep = int(request.form["sleep"])
    stress_freq = int(request.form["stress_freq"])
    anxiety = int(request.form["anxiety"])
    energy = int(request.form["energy"])
    social = int(request.form["social"])
    overwhelm = int(request.form["overwhelm"])
    exercise = int(request.form["exercise"])
    screen = int(request.form["screen"])

    score = (
        (10 - stress) * 2 +
        sleep * 2 +
        (5 - stress_freq) * 2 +
        (4 - anxiety) * 2 +
        energy * 2 +
        (4 - social) * 2 +
        (4 - overwhelm) * 2 +
        (4 - exercise) * 2 +
        (10 - screen)
    )

    if score >= 70:
        status = "Healthy"
        message = "Your mental health indicators are positive. Maintain this balance."
    elif score >= 45:
        status = "Moderate"
        message = "There are some concerns. Improving sleep and reducing stress will help."
    else:
        status = "Critical"
        message = "You may be experiencing high stress. Consider talking to someone or taking rest."

    return render_template("result.html", score=score, status=status, message=message)


def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)