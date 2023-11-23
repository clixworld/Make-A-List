from openai import OpenAI

class ChatGPT():
    def messages(self):
        client = OpenAI()
        completion = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
            ]
        )
        print(completion.choices[0].message)

