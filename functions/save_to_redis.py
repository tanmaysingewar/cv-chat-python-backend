from functions.get_key_value_pairs import get_key_value_pairs
def save_to_redis(bot_response,redis_client,relative_info,personality):
    print(bot_response,personality)

    data_string = get_key_value_pairs(bot_response,relative_info)
    # Parse the input string
    entries = data_string.split("\n")
    
    for entry in entries:
        if "Value:" in entry:
            # Split the entry into key and value
            key, value = entry.split("Value:", 1)
            key = key.strip()  # Extract the key
            value = value.strip()  # Extract the value
            
            # Debug print statement to simulate saving to Redis
            print(f"Saving key: {personality + ':' + key}, value: {value} to Redis...")

            key = personality + ':' + key
            # Uncomment below line to actually save in Redis
            redis_client.set(key, value)
    
    return "Data successfully saved to Redis."

_all_ =[
    "save_to_redis"
]