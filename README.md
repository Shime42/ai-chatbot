# University AI Chatbot

A Flask-based AI chatbot for university information, featuring OpenAI integration and a local knowledge base.

## Features

- User authentication system (login, registration)
- AI-powered chatbot with hybrid response system:
  - Local knowledge base for common questions
  - OpenAI integration for more complex queries
  - TF-IDF vectorization for finding similar questions
- Admin dashboard for managing:
  - Users
  - Knowledge base
  - Feedback
- User feedback system
- Chat history tracking

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MySQL Server
- OpenAI API key

### Installation

1. Clone the repository or download the source code

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key as an environment variable:
   ```
   # On Windows
   set OPENAI_API_KEY=your_api_key_here
   
   # On macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   ```

4. Initialize the MySQL database and train the model:
   ```
   python setup.py
   ```
   
   During setup, you will be prompted to enter your MySQL credentials and database name.

### Training the Model with Sample Data

To train the model with the provided sample knowledge base:

```
python train_model.py sample_knowledge.csv
```

You can also create your own CSV file with questions and answers to train the model.

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

3. Register a new account or log in with existing credentials

4. Use the chat interface to interact with the AI chatbot

## Admin Access

To create an admin account, register a new user and then update the user's role in the database:

```python
# Run this in a Python shell with the Flask app context
from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='your_username').first()
    user.role = 'admin'
    db.session.commit()
```

Admins can access the admin dashboard to manage users, knowledge base, and view feedback.

## Database Structure

The application uses MySQL to store the following data:

- **Users**: Store user information and authentication details
- **ChatbotKnowledge**: Knowledge base for the chatbot
- **Feedback**: User feedback on chatbot performance
- **ChatHistory**: Record of user-chatbot interactions

### Database Configuration

The MySQL database connection can be configured using environment variables:

- `DB_HOST`: MySQL server hostname (default: localhost)
- `DB_USER`: MySQL username (default: root)
- `DB_PASSWORD`: MySQL password (default: empty)
- `DB_NAME`: Database name (default: university_chatbot)

You can set these variables in your environment or they will be prompted during setup.

## AI Model

The chatbot uses a hybrid approach:

1. **TF-IDF Vectorization**: Converts questions to vectors for similarity matching
2. **Cosine Similarity**: Finds the most similar questions in the knowledge base
3. **OpenAI Integration**: Used when no good match is found in the knowledge base



