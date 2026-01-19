import os
import sys
import subprocess

def verify_openai_api_key():
    """Verify and fix OpenAI API key configuration"""
    print("\n===== OpenAI API Key Verification =====\n")
    
    # Check if OpenAI package is installed
    try:
        import openai
        print("✓ OpenAI package is installed.")
    except ImportError:
        print("✗ OpenAI package is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
            import openai
            print("✓ OpenAI package installed successfully.")
        except Exception as e:
            print(f"✗ Failed to install OpenAI package: {e}")
            return False
    
    # Check for OpenAI API key in environment
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("✗ OpenAI API key not found in environment variables.")
        key = input("Enter your OpenAI API key: ").strip()
        if key:
            # Set environment variable for current session
            os.environ['OPENAI_API_KEY'] = key
            
            # Set for future sessions
            if os.name == 'nt':  # Windows
                os.system(f'setx OPENAI_API_KEY "{key}"')
                print("✓ OpenAI API key set for future sessions.")
                print("For the current session, the key has been set in memory.")
            else:  # macOS/Linux
                with open(os.path.expanduser("~/.bashrc"), "a") as f:
                    f.write(f'\nexport OPENAI_API_KEY="{key}"\n')
                print("✓ OpenAI API key added to ~/.bashrc.")
                print("Run 'source ~/.bashrc' to apply for the current session.")
            
            # Verify the key works
            try:
                # Use the new client-based API format
                client = openai.OpenAI(api_key=key)
                # Simple API call to verify the key works
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print("✓ OpenAI API key verified and working correctly!")
                return True
            except Exception as e:
                print(f"✗ API key verification failed: {e}")
                print("Please check your API key and try again.")
                return False
        else:
            print("⚠ No API key provided. OpenAI integration will not work.")
            return False
    else:
        print("✓ OpenAI API key found in environment variables.")
        
        # Verify the key works
        try:
            # Use the new client-based API format
            client = openai.OpenAI(api_key=api_key)
            # Simple API call to verify the key works
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✓ OpenAI API key verified and working correctly!")
            return True
        except Exception as e:
            print(f"✗ API key verification failed: {e}")
            print("Your API key may be invalid or expired.")
            
            # Prompt for a new key
            key = input("Enter a new OpenAI API key (or press Enter to skip): ").strip()
            if key:
                # Set environment variable for current session
                os.environ['OPENAI_API_KEY'] = key
                
                # Set for future sessions
                if os.name == 'nt':  # Windows
                    os.system(f'setx OPENAI_API_KEY "{key}"')
                    print("✓ OpenAI API key set for future sessions.")
                else:  # macOS/Linux
                    with open(os.path.expanduser("~/.bashrc"), "a") as f:
                        f.write(f'\nexport OPENAI_API_KEY="{key}"\n')
                    print("✓ OpenAI API key added to ~/.bashrc.")
                    print("Run 'source ~/.bashrc' to apply for the current session.")
                
                # Verify the new key works
                try:
                    # Use the new client-based API format
                    client = openai.OpenAI(api_key=key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    print("✓ New OpenAI API key verified and working correctly!")
                    return True
                except Exception as e:
                    print(f"✗ New API key verification failed: {e}")
                    print("Please check your API key and try again.")
                    return False
            else:
                print("⚠ No new API key provided. OpenAI integration will not work.")
                return False

if __name__ == "__main__":
    verify_openai_key()