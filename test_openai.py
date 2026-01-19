import os
import openai

# Check if API key is set in environment variables
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    print("ERROR: OpenAI API key not found in environment variables.")
    exit(1)

print(f"API key found: {api_key[:5]}...{api_key[-4:]}")

try:
    # Initialize the client with the API key
    client = openai.OpenAI(api_key=api_key)
    
    # Make a simple test request
    print("Testing OpenAI API with a simple request...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    
    # Print the response
    print("\nAPI Response:")
    print(response)
    print("\nResponse content:")
    print(response.choices[0].message.content)
    
    print("\n✓ OpenAI API is working correctly!")
    
except Exception as e:
    print(f"\n✗ Error using OpenAI API: {e}")
    print("\nPlease check your API key and try again.")