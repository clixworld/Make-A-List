import openai
import os
from dotenv import load_dotenv


class ChatGPT():
    load_dotenv()
    def messages(self, user_input):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        completion = openai.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are a helpful assistant returning a grocery list with only up to 7 specifics ingredients based on the meal people want to make. Return each ingredient all lower case inside a python list such as [{'name': 'ingredient', 'amount':'total of the ingredient and fractions are in decimal up to the hundreth decimal place', 'type':'type of measurement'},{'name': 'ingredient', 'amount':'total of the ingredient and fractions are in decimal up to the hundreth decimal place, 'type':'type of measurement'}]. No other words besides the list because its for a program. Also no elipsis because it causes an error. Also make sure their double quoted. Also don't return words as plural or basically with no s at the end. For all proteins, use ounces"},
                {"role": "user", "content": user_input}
            ]
        )
        print(completion.choices[0].message.content)
        return(completion.choices[0].message.content)
