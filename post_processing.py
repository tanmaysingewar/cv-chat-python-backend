#postprocessing
from datetime import datetime

# Configure logging for the application
import logging

from datetime import datetime
from utils import call_groq_api

logging.basicConfig(
    filename="app.log",  # Log file name
    filemode='a',  # Append to log file
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',  # Log format
    datefmt='%H:%M:%S',  # Time format in logs
    level=logging.INFO  # Log level: INFO
)

def log_to_supabase(supabase,user_question, bot_response, cit=None, drt=None, rgt=None, personality=None, llm=None,relative_info=None):
    """
    Logs chatbot interaction details to Supabase.

    Args:
        supabase (Client): Supabase client instance for database operations.
        user_question (str): The user's question.
        bot_response (str): Chatbot's response to the user.
        cit (str, optional): Citation or source for any relevant information.
        drt (float, optional): Data retrieval time in milliseconds.
        rgt (float, optional): Response generation time in milliseconds.
        personality (str, optional): Chatbot's personality or profile.
        llm (str, optional): Language model used for generating the response.
        relative_info (str, optional): Additional context used in the response.

    Returns:
        None

    Example:
        Input:
            supabase = <supabase_client>
            user_question = "Who is the Prime Minister of India?"
            bot_response = "The Prime Minister of India is Narendra Modi."
            cit = "https://example.com/pm-info"
            drt = 45.2
            rgt = 123.4
            personality = "Delhi"
            llm = "meta-llama/llama-3.1-70b-instruct"
            relative_info = "PM of India is Narendra Modi since 2014."

        Output:
            None (Logs the data to Supabase and logs success/failure in the application logs.)
    """
    try:
        # Prepare data to insert
        data = {
            "user_question": user_question,
            "bot_response": bot_response,
            "cit": cit,
            "drt": drt,
            "rgt": rgt,
            "personality": personality,
            "llm": llm,
            "relative_data" : relative_info,
            "timestamp": datetime.utcnow().isoformat()  # ISO format for timestamp
        }

        # Insert into Supabase
        response = supabase.table("chatbot_logs").insert(data).execute()
        logging.info(f"Logged to Supabase: {response}")
    except Exception as e:
        logging.info(f"Error logging to Supabase: {e}")


def get_key_value_pairs(response,relative_info):
    """
    Converts a chatbot response into key-value pairs based on specific categories.

    Args:
        response (str): Chatbot's response to the user.
        relative_info (str): Existing contextual information to avoid duplicates.

    Returns:
        str: A string representation of key-value pairs to be stored or updated.

    Example:
        Input:
            response = "My dad runs a bookstore in Connaught Place, specializing in rare comics."
            relative_info = "relationships:father:business Value:bookstore"
        Output:
            "relationships:father:location Value:Connaught Place\nrelationships:father:specialty Value:rare comics"
    """
    # Define the prompt for the API call
    get_key_value_pairs_prompt = """
        ## Instruction
        - You are a helpful assistant that can save information to the Redis database.
        - Your job is to convert the given response into a consistent format and store it as key-value pairs in the Redis database.

       ## Key Selection Categories:
            - general: Response about general information.
            - skills: Response about specific skills or abilities.
            - interests: Response about likes, hobbies.
            - relationships: Response about family, friends, or social connections.
            - emotion: Response regarding feelings or emotional state.
            - knowledge: Response about facts or general information.
            - memory: Response that requires recall of past information.
            - tasks: Response about specific actions or plans.
            - goals: Response about objectives, aspirations, or future plans.
            - preferences: Response about personal choices or inclinations.
            - opinions: Response requesting personal thoughts or views.
            - habits: Response about routines, patterns, or regular actions.
            - thoughts: Questions that require reflection or self-evaluation.
        ## Guidelines for Response Processing:
        - Verify Existing Information: Before adding a key-value pair, check the provided relativeInfo to ensure the information does not already exist.
        - Format Consistently:Ensure the response is converted into a concise, consistent format while retaining its original meaning.
        - Avoid Duplicates: Only store new information or add specificity to existing entries.
        - Output Only Key-Value Pairs: Do not include additional text or explanations in the response.
        - try to store as much minimum information as possible, no long dialogues just pure info only.
        - If no information need to save just respond with : No info saved to Redis

        ## Already Stored Information
        ${relativeInfo}

        ##Input:
        ${response}

        ## Output:
        For new information: Add the key-value pair.
        For duplicate or similar entries: Skip or update as required.
        Here’s an example of how this revised prompt works:

        # Example 1 
        ## Input:
        "Arre bhai, my dad's a shopkeeper in Karol Bagh, he sells some amazing fabrics and textiles, been running the shop for over 20 years, real Dilliwalah spirit yaar!"

        ## Already Stored Information:
            relationships:business Value:shopkeeper
            relationships:father:location Value:Karol Bagh

        ## Output:
            relationships:father:products Value:fabrics and textiles

        #Example 2
        ## Input:
        "Arre, my mom's a total foodie, bhai! She runs a small parantha joint in Paranthe Wali Gali, and her paranthas are to die for, ek dum famous!"

        ## Already Stored Information:
            relationships:mother:nature Value:foodie

        ## Output:
            relationships:mother:business Value: a paratha joint
            relationships:mother:location  Value: Paranthe Wali Gali
    ## User Response
    {response}
    """.replace("{response}", response).replace("{relative_info}",relative_info)

    # Call the API with the prompt
    key_vale_pair = call_groq_api(get_key_value_pairs_prompt)
    return key_vale_pair


def save_to_redis(bot_response,redis_client,relative_info,personality):
    """
    Saves key-value pairs extracted from a chatbot response into Redis.

    Args:
        bot_response (str): Chatbot's response to the user.
        redis_client (Redis): Redis client instance for database operations.
        relative_info (str): Existing contextual information to avoid duplicate storage.
        personality (str): Chatbot's personality or profile.

    Returns:
        str: A message indicating success or failure in saving data to Redis.

    Example:
        Input:
            bot_response = "My dad's a chef in Chandni Chowk, specializing in Mughlai food."
            relative_info = "relationships:father:profession Value:chef"
            personality = "delhi"

        Output:
            "Data successfully saved to Redis."
    """
    try : 
        # Get the key value pairs from the bot response
        data_string = get_key_value_pairs(bot_response,relative_info)
        # Parse the input string
        entries = data_string.split("\n")
        
        for entry in entries:
            if "Value:" in entry:
                # Split the entry into key and value
                key, value = entry.split("Value:", 1)
                key = key.strip()  # Extract the key
                value = value.strip()  # Extract the value
                
                # Logging print statement to simulate saving to Redis
                logging.info(f"Saving key: {personality + ':' + key}, value: {value} to Redis...")

                # Prepare the key for Redis Search
                key = personality + ':' + key

                # Save the key-value pair to Redis
                redis_client.set(key, value)
                
        logging.info(f"Redis save :{entries}")
        return "Data successfully saved to Redis."
    except Exception as e:
        logging.info(f"Error saving data to Redis: {e}")

_all_ =[
    "save_to_redis","log_to_supabase","get_key_value_pairs"
]

