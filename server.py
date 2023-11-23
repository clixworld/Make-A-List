from flask import Flask, render_template
from chatgpt import ChatGPT

ai_bot = ChatGPT()
app = Flask(__name__)

@app.route('/')
def home():
    attempt = ai_bot.messages()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)