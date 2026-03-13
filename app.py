from flask import Flask, render_template, request
import webbrowser
import threading

app = Flask(__name__)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():
    name = request.form["name"]
    return render_template("dashboard.html", name=name)


@app.route("/result", methods=["POST"])
def result():

    stress = int(request.form["stress"])
    sleep = int(request.form["sleep"])

    score = (stress + sleep) * 5

    if score < 40:
        status = "Low Stress"
        message = "You seem relaxed. Keep maintaining a healthy routine."
    elif score < 70:
        status = "Moderate Stress"
        message = "Try taking short breaks and practicing mindfulness."
    else:
        status = "High Stress"
        message = "Consider resting more and talking to someone you trust."

    return render_template(
        "result.html",
        score=score,
        status=status,
        message=message
    )



def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
