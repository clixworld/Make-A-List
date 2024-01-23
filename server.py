from flask import Flask, render_template, request
from chatgpt import ChatGPT
import ast
import smtplib
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
ai_bot = ChatGPT()
app = Flask(__name__)

saved_ingredients = {} 
current_ingredients = [] 


def combine_ingredients(existing, new):
    if new is not None:
        for ingredient in new:
            name = ingredient['name']
            amount = float(ingredient['amount'])
            measurement_type = ingredient.get('type', 'unknown')

            key = f"{name}_{measurement_type}"
            existing[key] = round(existing.get(key, 0) + amount, 2)

    return existing

@app.route('/', methods=['POST', 'GET'])
def home():
    global current_ingredients, saved_ingredients
    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients)

@app.route('/current_ingredients', methods=['POST'])
def current_ingredient():
    global saved_ingredients, current_ingredients

    user_input = request.form['recipe']
    attempt_str = ai_bot.messages(user_input)
    current_ingredients = ast.literal_eval(attempt_str)

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients, save_option=True, send_email_opt=True)

@app.route('/save_ingredients', methods=['POST'])
def save_ingredients():
    global saved_ingredients, current_ingredients

    recipe_text = request.form.get('recipe_text', '')
    try:
        current_ingredients = ast.literal_eval(recipe_text)
        saved_ingredients = combine_ingredients(saved_ingredients, current_ingredients)
    except Exception as e:
        print("Error processing recipe_text:", e)

    current_ingredients = []

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients, send_email_opt=True)

@app.route('/send_email', methods=['POST'])
def send_message():
    global saved_ingredients

    user_email = request.form["email"]
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

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients, send_email_opt=True)

    

if __name__ == "__main__":
    app.run(debug=False)