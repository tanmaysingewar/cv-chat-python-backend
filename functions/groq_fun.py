import requests
import os
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

def call_groq_api(prompt,model="meta-llama/llama-3.1-70b-instruct"):
    client = OpenAI(
        base_url="https://api.novita.ai/v3/openai",
        # Get the Novita AI API Key by referring to: https://novita.ai/docs/get-started/quickstart.html#_2-manage-api-key.
        api_key= os.getenv("NOVITA_API_KEY"),
    )

    model = "meta-llama/llama-3.1-70b-instruct"
    stream = False 

    chat_completion_res = client.chat.completions.create(
        model=model,
        messages=[
             {
                "role": "user",
                "content": prompt
            }
        ],
        stream=stream,
    )

    return chat_completion_res.choices[0].message.content

_all_ = [
    "call_groq_api"
]