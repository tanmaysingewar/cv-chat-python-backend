import requests
import os
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv()

url = "https://api.perplexity.ai/chat/completions"

def call_groq_api(prompt,model="llama-3.1-sonar-large-128k-online"):
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        return json_response.get("choices")[0].get("message").get("content")
    elif response.status_code == 429:
        return response.status_code
    elif response.status_code == 400:
        return response.status_code
    else:
        return False

_all_ = [
    "call_groq_api"
]