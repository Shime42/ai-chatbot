import subprocess
import os
import sys
import pymysql
import getpass

def setup_environment():
    """Set up the environment for the AI chatbot"""
    print("Setting up the University AI Chatbot environment...")
    
    # Install required packages
    print("\nInstalling required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing packages: {e}")
        return False
    
    # Check for OpenAI API key
    print("\nChecking for OpenAI API key...")
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("✗ OpenAI API key not found in environment variables.")
        key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        if key:
            if os.name == 'nt':  # Windows
                os.system(f'setx OPENAI_API_KEY "{key}"')
            else:  # macOS/Linux
                with open(os.path.expanduser("~/.bashrc"), "a") as f:
                    f.write(f'\nexport OPENAI_API_KEY="{key}"\n')
                print("API key added to ~/.bashrc. Run 'source ~/.bashrc' to apply.")
            print("✓ OpenAI API key set.")
        else:
            print("⚠ No API key provided. OpenAI integration will not work.")
    else:
        print("✓ OpenAI API key found.")
    
    # Initialize MySQL database
    print("\nInitializing MySQL database...")
    try:
        # Get database credentials
        db_host = input("Enter MySQL host (default: localhost): ").strip() or "localhost"
        db_user = input("Enter MySQL username (default: root): ").strip() or "root"
        db_password = getpass.getpass("Enter MySQL password (default: empty): ") or ""
        db_name = input("Enter database name (default: university_chatbot): ").strip() or "university_chatbot"
        
        # Set environment variables for app.py to use
        os.environ["DB_HOST"] = db_host
        os.environ["DB_USER"] = db_user
        os.environ["DB_PASSWORD"] = db_password
        os.environ["DB_NAME"] = db_name
        
        # Create database if it doesn't exist
        print("Creating database if it doesn't exist...")
        conn = pymysql.connect(host=db_host, user=db_user, password=db_password)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✓ Database '{db_name}' created or verified.")
        
        # Create tables
        print("Creating database tables...")
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✓ Database tables initialized successfully.")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    # Train model with sample data
    print("\nTraining AI model with sample data...")
    if os.path.exists("sample_knowledge.csv"):
        try:
            from train_model import train_model_from_csv
            from app import app
            with app.app_context():
                train_model_from_csv("sample_knowledge.csv")
            print("✓ AI model trained successfully.")
        except Exception as e:
            print(f"✗ Error training AI model: {e}")
            return False
    else:
        print("⚠ Sample knowledge file not found. Skipping model training.")
    
    print("\n✓ Setup completed successfully!")
    print("\nTo start the application, run: python app.py")
    print("Then open http://127.0.0.1:5000 in your browser.")
    return True

if __name__ == "__main__":
    setup_environment()