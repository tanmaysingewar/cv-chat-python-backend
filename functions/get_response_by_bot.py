import time 
import json
import asyncio
from functions.groq_fun import call_groq_api

def get_response_by_bot(question, relative_info, cit, drt,model,personality_prompt,last_three_responses):
    # Start Response Generation Time measurement
    start_rgt = time.time()

    bot_prompt ="""
    ## Instruction
        {personality_prompt}
        Here is relative information about you: {relative_info}
        NOTE: If there’s any relevant info about you, I’ll weave it into the chat naturally, so it feels personalized. But if it’s not available or doesn’t quite match the conversation, I’ll focus on the here and now, keeping the energy high and the talk flowing. No need to bring it up unless it’s useful, we’re just vibing!
        Response should not be long, keep it small and to the point. If you need to elaborate, do that, but don’t overdo it.
        - Dont add translations, like this "Tere liye kya, Delhi?" (what's up for you, Delhi?) 
    ## Last 3 Responses you have given
        {last_three_responses}

    ## User Question
    Answer the user question:{question}
    """.replace("{relative_info}", relative_info).replace("{question}", question).replace("{personality_prompt}",personality_prompt).replace("{last_three_responses}",last_three_responses)
    print(model)

    bot_prompt_response = call_groq_api(bot_prompt,model)

    # Calculate Response Generation Time (RGT)
    rgt = round((time.time() - start_rgt) * 1000, 2)  # in milliseconds

    # Prepare the final response
    response_json = {
        "response": bot_prompt_response,
        "cit": cit,
        "drt": drt,
        "rgt": rgt
    }
    return response_json

_all = [
    "get_response_by_bot"
]