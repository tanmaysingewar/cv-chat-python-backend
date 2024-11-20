from functions.groq_fun import call_groq_api
import time 

# Relative information search
def get_relative_info(question,r,personality):
    start_time = time.time()
    
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
            - opinions: Questions requesting personal thoughts or views.
            - habits: Questions about routines, patterns, or regular actions.
        
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
    res = call_groq_api(relative_info_prompt)


    # Calculate Category Identification Time (CIT)
    cit = round((time.time() - start_time) * 1000, 2)  # in milliseconds
    start_drt = time.time()
    response = ""
    if res != "NO":
        res = personality + ":" + res + ":*"
        print(f"relative info prompt: {res}")

        # Start Data Retrieval Time measurement
      

        cursor = 0
        result = {}

        # Scan loop
        while True:
            cursor, batch = r.scan(cursor=cursor, match=res)
            
            for key in batch:
                key_str = key.decode('utf-8')  # Decode byte key to string
                result[key_str] = r.get(key).decode('utf-8')  # Get string value
            
            if cursor == 0:
                break
                # get values in variable

        # Print results
        for key, value in result.items():
            response += f"{key} - {value}\n"

    # Calculate Data Retrieval Time (DRT)
    drt = round((time.time() - start_drt) * 1000, 2)  # in milliseconds
    
    return response, cit, drt

_all_ = [
    "get_relative_info"
]