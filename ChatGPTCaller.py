from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def call_chatgpt(question, prompt):
    openaiclient = OpenAI()
    response = openaiclient.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content