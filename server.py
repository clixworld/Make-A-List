from flask import Flask, render_template, request, session
from chatgpt import ChatGPT
import ast
import smtplib
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from threading import Lock

ai_bot = ChatGPT()
app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.environ.get("OPENAI_API_KEY")

app.config['SAVED_INGREDIENTS_LOCK'] = threading.Lock()
app.config['CURRENT_INGREDIENTS_LOCK'] = threading.Lock()
saved_ingredients_lock = Lock()

def combine_ingredients(existing, new):
    if new is not None:
        for ingredient in new:
            name = ingredient['name']
            amount = float(ingredient['amount'])
            measurement_type = ingredient.get('type', 'unknown')

            key = f"{name}_{measurement_type}"
            
            with saved_ingredients_lock:
                if key in existing:
                    existing[key] += amount
                else:
                    existing[key] = amount

    return existing

@app.route('/', methods=['POST', 'GET'])
def home():
    saved_ingredients = session.get('saved_ingredients', {})

    with app.config['CURRENT_INGREDIENTS_LOCK']:
        current_ingredients = session.get('_current_ingredients', [])
        session['_current_ingredients'] = current_ingredients  

    save_option = bool(current_ingredients)
    clear_button = bool(saved_ingredients)

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients, send_email_opt=True, save_option=save_option, clear_button=clear_button)



@app.route('/current_ingredients', methods=['POST'])
def current_ingredient():
    user_input = request.form['recipe']
    attempt_str = ai_bot.messages(user_input)
    current_ingredients = ast.literal_eval(attempt_str)

    with app.config['CURRENT_INGREDIENTS_LOCK']:
        session['_current_ingredients'] = current_ingredients

    save_option = bool(current_ingredients)
    clear_button = bool(session.get('saved_ingredients', {}))

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=session.get('saved_ingredients', {}), send_email_opt=True, save_option=save_option, clear_button=clear_button)


@app.route('/save_ingredients', methods=['POST'])
def save_ingredients():
    try:
        with app.config['CURRENT_INGREDIENTS_LOCK']:
            current_ingredients = session.get('_current_ingredients', [])


        with app.config['SAVED_INGREDIENTS_LOCK']:
            session['saved_ingredients'] = combine_ingredients(session.get('saved_ingredients', {}).copy(), current_ingredients)

            session['_current_ingredients'] = []

    except Exception as e:
        print("Error processing current_ingredients:", e)

    save_option = bool(session.get('_current_ingredients', []))
    clear_button = bool(session.get('saved_ingredients', {}))

    return render_template("index.html", attempt=[], saved_ingredients=session.get('saved_ingredients', {}), send_email_opt=True, save_option=save_option, clear_button=clear_button)


@app.route('/clear_ingredients', methods=['POST'])
def clear_ingredients():

    with app.config['SAVED_INGREDIENTS_LOCK']:
        session['saved_ingredients'] = {}

    save_option = bool(session.get('_current_ingredients', []))
    clear_button = bool(session.get('saved_ingredients', {}))

    return render_template("index.html", attempt=session['_current_ingredients'], saved_ingredients=session['saved_ingredients'], send_email_opt=True, save_option=save_option, clear_button=clear_button)


@app.route('/send_email', methods=['POST'])
def send_message():
    user_email = request.form["email"]

    with app.config['SAVED_INGREDIENTS_LOCK']:
        saved_ingredients = session.get('saved_ingredients', {})
        session['_saved_ingredients'] = saved_ingredients

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
        
        message = MIMEMultipart()
        message["From"] = os.getenv("EMAIL")
        message["To"] = user_email
        message["Subject"] = "Make-A-List"

        body = "Your Saved ingredients:\n\n"
        for key, value in saved_ingredients.items():
            body += f"{key}:{value}\n"

        message.attach(MIMEText(body, "plain"))

        connection.sendmail(from_addr=os.getenv("EMAIL"), to_addrs=user_email, msg=message.as_string())

    save_option = bool(session.get('_current_ingredients', []))
    clear_button = bool(session.get('saved_ingredients', {}))

    return render_template("index.html", attempt=session.get('_current_ingredients', []), saved_ingredients=saved_ingredients, send_email_opt=True, save_option=save_option, clear_button=clear_button)


if __name__ == "__main__":
    app.run(debug=False)
