import os
import sys
from groq import Groq
from dotenv import load_dotenv

def verify_groq():
    print("Verifying Groq Setup...")
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ Error: GROQ_API_KEY environment variable is NOT set.")
        print("Please set it directly or in your .env file.")
        return False
    
    print(f"✅ GROQ_API_KEY found (starts with {api_key[:4]}...)")
    
    try:
        client = Groq(api_key=api_key)
        print("Attempting simple chat completion...")
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_completion_tokens=20
        )
        print("✅ API Call Successful!")
        print(f"Response: {completion.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return False

if __name__ == "__main__":
    if verify_groq():
        sys.exit(0)
    else:
        sys.exit(1)
