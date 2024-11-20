import redis
from fastapi import FastAPI,File,UploadFile,Form,BackgroundTasks
from pydantic import BaseModel
from typing_extensions import Annotated
from typing import Union
import json

import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

from functions.groq_fun import call_groq_api
from functions.get_key_value_pairs import get_key_value_pairs
from functions.get_relative_info import get_relative_info
from functions.save_to_redis import save_to_redis
from functions.get_response_by_bot import get_response_by_bot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(os.getenv('REDIS_HOST'))

redis_client = redis.Redis(
  host=os.getenv('REDIS_HOST'),
  port=6379,
  password=os.getenv('REDIS_PASSWORD'),
  ssl=True,
  db=0
)

class QuestionRequest(BaseModel):
    question: Union[str, None] = None
    llm: str = "llama-3.1-70b-versatile"
    personality : str = "delhi"
    personality_prompt : str = ""
    last_three_responses : str = ""

@app.post("/cv/chat")
async def cv_chat(request: QuestionRequest,background_tasks: BackgroundTasks):
    try:
        print(request.question)
        if not request.question or request.question.strip() == "":
            return {"error": str("Please provide a question")}

        # Get relative info with timing
        relative_info, cit, drt = get_relative_info(request.question, redis_client,request.personality)
        print(relative_info)

        print(request.last_three_responses)

        bot_response = get_response_by_bot(request.question, relative_info, cit, drt,request.llm,request.personality_prompt,request.last_three_responses)

        # Make sure bot_response is a dictionary and access the response key
        if isinstance(bot_response, dict) and "response" in bot_response:
            response_data = bot_response["response"]
        else:
            return {"error": "Bot response format is invalid"}

        # Save bot response to Redis asynchronously
        background_tasks.add_task(save_to_redis, response_data, redis_client,relative_info,request.personality)

        # Get bot response with timing metrics
        return bot_response
    
    except Exception as e:
        print(e)
        return {"error": str("Error occurred while generating the quiz and summary")}