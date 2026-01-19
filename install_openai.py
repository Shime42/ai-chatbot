import subprocess
import sys
import os

def install_openai():
    """Install OpenAI package and set up environment variables"""
    print("Installing OpenAI package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
        print("✓ OpenAI package installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing OpenAI package: {e}")
        return False
    
    # Check for OpenAI API key
    print("\nChecking for OpenAI API key...")
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("✗ OpenAI API key not found in environment variables.")
        key = input("Enter your OpenAI API key: ").strip()
        if key:
            if os.name == 'nt':  # Windows
                os.system(f'setx OPENAI_API_KEY "{key}"')
                print("✓ OpenAI API key set for future sessions.")
                print("For the current session, please set it manually:")
                print(f'set OPENAI_API_KEY={key}')
            else:  # macOS/Linux
                with open(os.path.expanduser("~/.bashrc"), "a") as f:
                    f.write(f'\nexport OPENAI_API_KEY="{key}"\n')
                print("✓ OpenAI API key added to ~/.bashrc.")
                print("Run 'source ~/.bashrc' to apply for the current session.")
        else:
            print("⚠ No API key provided. OpenAI integration will not work.")
    else:
        print("✓ OpenAI API key already set.")
    
    print("\nSetup completed!")
    return True

if __name__ == "__main__":
    install_openai()