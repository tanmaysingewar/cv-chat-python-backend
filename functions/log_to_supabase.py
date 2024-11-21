from datetime import datetime

def log_to_supabase(supabase,user_question, bot_response, cit=None, drt=None, rgt=None, personality=None, llm=None):
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
            "timestamp": datetime.utcnow().isoformat()  # ISO format for timestamp
        }

        # Insert into Supabase
        response = supabase.table("chatbot_logs").insert(data).execute()
        print("Logged to Supabase:", response)
    except Exception as e:
        print(f"Error logging to Supabase: {e}")

_all_ = ["log_to_supabase"]