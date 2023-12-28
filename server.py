from flask import Flask, render_template, request
from chatgpt import ChatGPT
import ast

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
            existing[key] = existing.get(key, 0) + amount

    return existing

@app.route('/', methods=['GET', 'POST'])
def home():
    global current_ingredients, saved_ingredients

    if request.method == 'POST':
        user_input = request.form['recipe']
        attempt_str = ai_bot.messages(user_input)
        current_ingredients = ast.literal_eval(attempt_str)

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients)


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

    return render_template("index.html", attempt=current_ingredients, saved_ingredients=saved_ingredients)

if __name__ == "__main__":
    app.run(debug=True)