
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
from supabase import create_client, Client

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

from utils import call_groq_api  
from pre_processing import get_relative_info

from model import get_response_by_bot

from post_processing import get_key_value_pairs
from post_processing import save_to_redis
from post_processing import log_to_supabase

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,  # Allow credentials (e.g., cookies, headers)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all HTTP headers
)

# Initialize Redis client with host, port, password, and SSL configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),  # Redis host from environment variable
    port=6379,  # Redis default port
    password=os.getenv('REDIS_PASSWORD'),  # Redis password from environment variable
    ssl=True,  # Use SSL for secure connection
    db=0  # Use database 0
)

# Supabase connection details
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Supabase project URL from environment variable
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Supabase API key from environment variable

# Configure logging for the application
import logging
logging.basicConfig(
    filename="app.log",  # Log file name
    filemode='a',  # Append to log file
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',  # Log format
    datefmt='%H:%M:%S',  # Time format in logs
    level=logging.INFO  # Log level: INFO
)

# Create a Supabase client using project URL and API key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define a Pydantic model for the incoming request body
class QuestionRequest(BaseModel):
    """
    Model for incoming question request data.
    
    Attributes:
        question (Union[str, None]): User's question. Default is None.
        llm (str): Language model to use for processing. Default is "meta-llama/llama-3.1-70b-instruct".
        personality (str): Personality type for the bot. Default is "delhi".
        personality_prompt (str): Custom personality prompt for the bot.
        last_three_responses (str): Contextual history from the last three responses.
    """
    question: Union[str, None] = None  # Question from the user
    llm: str = "meta-llama/llama-3.1-70b-instruct"  # Default language model
    personality: str = "delhi"  # Personality type
    personality_prompt: str = ""  # Personality prompt 
    last_three_responses: str = ""  # Context from last three responses

# Define the endpoint for chat functionality
@app.post("/cv/chat")
async def cv_chat(request: QuestionRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to handle chatbot queries.

    Args:
        request (QuestionRequest): Input data containing user's question and related configuration.
        background_tasks (BackgroundTasks): Tasks to be performed asynchronously.

    Returns:
        dict: A response from the chatbot or an error message if the process fails.

    Example:
        Input:
        {
            "question": "What is the history of Red Fort?",
            "llm": "meta-llama/llama-3.1-70b-instruct",
            "personality": "delhi",
            "personality_prompt": "",
            "last_three_responses": "Explained about Qutub Minar."
        }

        Output:
        {
             "response": "The Red Fort was constructed by Mughal Emperor Shah Jahan in 1648 as the palace of his fortified capital Shahjahanabad.",
            "cit": 4.34,
            "drt": 34.43,
            "rgt": 345.22
        }
    """
    try:
        # Validate if the question is provided and not empty
        if not request.question or request.question.strip() == "":
            return {"error": str("Please provide a question")}  # Return error if invalid

        # Get relative information and timing data for the question
        relative_info, cit, drt = get_relative_info(
            request.question, redis_client, request.personality
        )

        # Generate bot response using the provided information and language model
        bot_response = get_response_by_bot(
            request.question, relative_info, cit, drt, request.llm, request.personality_prompt, request.last_three_responses
        )

        # Ensure bot response is in the correct format (dictionary with a "response" key)
        if isinstance(bot_response, dict) and "response" in bot_response:
            response_data = bot_response["response"]
        else:
            return {"error": "Bot response format is invalid"}  # Return error if invalid

        # Log the input question, relative info, and bot response
        logging.info(f"Question: {request.question}")
        logging.info(f"Last 3 Responses: {request.last_three_responses}")
        logging.info(f"Relative Info: {relative_info}")
        logging.info(f"Response: {response_data}")

        # Save bot response and logs asynchronously
        background_tasks.add_task(
            save_to_redis, response_data, redis_client, relative_info, request.personality
        )
        background_tasks.add_task(
            log_to_supabase, supabase, request.question, response_data, cit, drt, bot_response["rgt"], request.personality, request.llm, relative_info
        )

        # Return the bot response
        return bot_response
    
    # Handle any exceptions that occur during execution
    except Exception as e:
        logging.info(f"Error: {e}")  # Log the error for debugging
        return {"error": str("Error occurred while generating the quiz and summary")}  # Return error message
