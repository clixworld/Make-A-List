from flask import Flask, render_template, request
from chatgpt import ChatGPT
import ast

ai_bot = ChatGPT()
app = Flask(__name__)

saved_ingredients = {} 
current_ingredients = [] 
recipe = None


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
    global current_ingredients, recipe, saved_ingredients

    if request.method == 'POST':
        user_input = request.form['recipe']
        attempt_str = ai_bot.messages(user_input)
        current_ingredients = ast.literal_eval(attempt_str)

        action = request.form.get('action', '')

        if action == 'generate':
            recipe = ai_bot.generate_recipe(current_ingredients)

        elif action == 'save':
            saved_ingredients = combine_ingredients(saved_ingredients, current_ingredients)
            print("Saved Ingredients:", saved_ingredients)


    return render_template("index.html", attempt=current_ingredients, recipe=recipe, saved_ingredients=saved_ingredients)


@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    global current_ingredients, recipe

    if recipe is None:
        recipe = ai_bot.generate_recipe(current_ingredients)

    return render_template("index.html", attempt=current_ingredients, recipe=recipe, saved_ingredients=saved_ingredients)

@app.route('/save_ingredients', methods=['POST'])
def save_ingredients():
    global saved_ingredients, current_ingredients

    recipe_text = request.form.get('recipe_text', '')
    current_ingredients = ast.literal_eval(recipe_text)
    saved_ingredients = combine_ingredients(saved_ingredients, current_ingredients)

    current_ingredients = []
    print("Saved Ingredients:", saved_ingredients)

    return render_template("index.html", attempt=current_ingredients, recipe=None, saved_ingredients=saved_ingredients)

if __name__ == "__main__":
    app.run(debug=True)