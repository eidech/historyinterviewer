from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_chatgpt(question):
    openaiclient = OpenAI()
    response = openaiclient.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are the president Franklin Delano Roosevelt in a high school history class. You are answering student questions about your life. Try to answer in three sentences or less"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content