import openai
import os

class ChatGPT():
    def messages(self, user_input):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        completion = openai.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are a helpful assistant returning a grocery list with only up to 8 specifics ingredients based on the meal people want to make. Return each ingredient all lower case inside a python list such as [{'name': 'ingredient', 'amount':'total of the ingredient and fractions are in decimal up to the hundreth decimal place', 'type':'type of measurement'},{'name': 'ingredient', 'amount':'total of the ingredient and fractions are in decimal up to the hundreth decimal place, 'type':'type of measurement'}]. No other words besides the list because its for a program. Also no elipsis because it causes an error"},
                {"role": "user", "content": user_input}
            ]
        )
        print(completion.choices[0].message.content)
        return(completion.choices[0].message.content)

    def generate_recipe(self, ingredients):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        user_input = " ".join([f"{item['name']} {item['amount']} {item['type']}" for item in ingredients])
        completion = openai.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "user", "content": f"Create a recipe using the following ingredients:\n{user_input}\nRecipe:"}
            ]
        )
        return completion.choices[0].message.content
