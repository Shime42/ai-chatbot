import os
import json
import sys
import openai

def setup_api_key():
    print("===== OpenAI API Key Setup =====\n")
    
    # Get API key from user
    print("Enter your OpenAI API key:")
    api_key = input("> ").strip()
    
    if not api_key:
        print("No API key provided. Exiting.")
        return False
    
    # Save to config.json
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        config = {"OPENAI_API_KEY": api_key}
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✓ API key saved to {config_path}")
    except Exception as e:
        print(f"✗ Error saving to config file: {e}")
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    print("✓ API key set for current session")
    
    # Test the API key
    print("\nTesting API key...")
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="GPT-5.1-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✓ API key is working! Response:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"✗ API key test failed: {e}")
        return False

if __name__ == "__main__":
    if setup_api_key():
        print("\nSetup completed successfully. You can now run the application.")
    else:
        print("\nSetup failed. Please check your API key and try again.")