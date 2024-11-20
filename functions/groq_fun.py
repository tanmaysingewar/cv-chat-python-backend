
from groq import Groq

# Initialize the Groq client
client = Groq(
    api_key="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"  # Replace with your actual API key
)

# Function to call Groq API with LLAMA 3 model
def call_groq_api(prompt, model="llama-3.1-70b-versatile"):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

_all_ = [
    "call_groq_api"
]