from utils import call_groq_api
import time 

# Relative information search
def get_relative_info(question,r,personality):
    """
    Searches for relevant information stored in Redis based on the user's question and predefined categories.

    Args:
        question (str): The user's question.
        r (Redis): Redis client instance for retrieving data.
        personality (str): The chatbot's personality or profile prefix for categorizing stored data.

    Returns:
        tuple:
            - response (str): Retrieved relevant information, formatted as key-value pairs.
            - cit (float): Category Identification Time in milliseconds.
            - drt (float): Data Retrieval Time in milliseconds.

    Example:
        Input:
            question = "What are your hobbies?"
            r = <Redis_client>
            personality = "delhi"

        Redis Data (Assuming Redis contains the following stored info):
            delhi:interests:reading - Loves novels and historical books
            delhi:interests:cooking - Enjoys experimenting with Mughlai recipes

        Output:
            response = "delhi:interests:reading - Loves novels and historical books\ndelhi:interests:cooking - Enjoys experimenting with Mughlai recipes\n"
            cit = 120.45  # (Example time in milliseconds)
            drt = 85.34   # (Example time in milliseconds)
    """
    # Start the timer
    start_time = time.time()
    
    # Create the prompt for the Relative Info Search 
    relative_info_prompt ="""
        ## Instruction
        - You are the highly skilled question categorizer who can categorize questions into categories based on the required information.
        - The categories are:  
            - general: Questions about the general information.
            - skills: Questions about specific skills or abilities.
            - interests: Questions about likes, hobbies, or preferences.
            - relationships: Questions about family, friends, or social connections.
            - emotion: Questions regarding feelings or emotional state.
            - knowledge: Questions about facts or general information.
            - memory: Questions that require recall of past information.
            - tasks: Questions about specific actions or plans.
            - goals: Questions about objectives, aspirations, or future plans.
            - preferences: Questions about personal choices or inclinations.
            - opinions: Questions requesting personal views.
            - habits: Questions about routines, patterns, or regular actions.
            - thoughts: Questions that require reflection or self-evaluation.
        
        - If the question belongs to any of the categories above, respond with the corresponding category. 
        - If the question does not belong to any category, respond with NO.

        Example:
        Input: What are your skills?
        Output: skills

        Input: What is your name?
        Output: general

        ## User Question  
        {question}

        --- 
    """.replace("{question}", question)

    # Call to LLM to get the response 
    res = call_groq_api(relative_info_prompt)


    # Calculate Category Identification Time (CIT)
    cit = round((time.time() - start_time) * 1000, 2)  # in milliseconds
    start_drt = time.time()
    response = ""

    # If response is NO then there No matching category tin that information is stored else we get the category
    if res != "NO":
        res = personality + ":" + res + ":*"

        cursor = 0
        result = {}

        # Scan loop
        while True:
            cursor, batch = r.scan(cursor=cursor, match=res)
            
            # get values in variable
            for key in batch:
                key_str = key.decode('utf-8')  # Decode byte key to string
                result[key_str] = r.get(key).decode('utf-8')  # Get string value
            
            if cursor == 0:
                break

        # Print results
        for key, value in result.items():
            response += f"{key} - {value}\n"

    # Calculate Data Retrieval Time (DRT)
    drt = round((time.time() - start_drt) * 1000, 2)  # in milliseconds
    
    return response, cit, drt



_all_ = [
    "get_relative_info"
]
