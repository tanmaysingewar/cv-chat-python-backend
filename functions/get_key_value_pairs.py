from functions.groq_fun import call_groq_api

# save info to the database
def get_key_value_pairs(response,relative_info):
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

    key_vale_pair = call_groq_api(get_key_value_pairs_prompt)
    print(key_vale_pair)
    return key_vale_pair

_all_ = [
    "get_key_value_pairs"
]