import os
import openai
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import ChatbotKnowledge, ChatHistory
from app import db
import json

# Try multiple methods to get the OpenAI API key
def get_api_key():
    # First check environment variable
    api_key = os.environ.get('OPENAI_API_KEY')
    
    # If not found, try to read from a config file
    if not api_key:
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('OPENAI_API_KEY')
                    if api_key:
                        # Set it in environment for current session
                        os.environ['OPENAI_API_KEY'] = api_key
                        print("OpenAI API key loaded from config file.")
        except Exception as e:
            print(f"Error reading config file: {e}")
    
    return api_key

# Get API key using our robust method
api_key = get_api_key()

# Initialize OpenAI client
openai_client = None
if api_key:
    try:
        openai_client = openai.OpenAI(api_key=api_key)
        print("OpenAI client initialized successfully.")
    except Exception as e:
        print(f"ERROR initializing OpenAI client: {e}")
        print("Some features may not work properly.")
else:
    print("WARNING: OpenAI API key not found. Some features may not work.")
    print("Run 'python verify_openai.py' to set up your API key.")

class AIModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.knowledge_base = None
        self.vectors = None
        self.trained = False
    
    def train(self):
        """Train the model using the knowledge base from the database"""
        # Get all knowledge base entries from the database
        knowledge_entries = ChatbotKnowledge.query.all()
        
        if not knowledge_entries:
            print("No knowledge base entries found for training.")
            return False
        
        # Extract questions for training
        questions = [entry.question for entry in knowledge_entries]
        self.knowledge_base = knowledge_entries
        
        # Create TF-IDF vectors for questions
        self.vectors = self.vectorizer.fit_transform(questions)
        self.trained = True
        print(f"Model trained with {len(questions)} knowledge base entries.")
        return True
    
    def find_similar_question(self, user_query):
        """Find the most similar question in the knowledge base"""
        if not self.trained:
            return None, 0
        
        # Transform user query to vector
        query_vector = self.vectorizer.transform([user_query])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(query_vector, self.vectors)[0]
        
        # Find the most similar question
        max_score_index = np.argmax(similarity_scores)
        max_score = similarity_scores[max_score_index]
        
        # Return the most similar knowledge entry and its similarity score
        if max_score > 0.5:  # Threshold for similarity
            return self.knowledge_base[max_score_index], max_score
        return None, 0
    
    def get_openai_response(self, user_query, context=None):
        """Get a response from OpenAI API"""
        # Check if OpenAI client is initialized
        if not openai_client:
            print("ERROR: OpenAI client is not initialized. Cannot generate response.")
            return "I'm having trouble connecting to my knowledge base. Please ask an administrator to check the OpenAI API key configuration."
            
        try:
            # Prepare messages for the API
            messages = [
                {"role": "system", "content": "You are a helpful university assistant chatbot. Provide concise and accurate information to student queries."}
            ]
            
            # Add context from knowledge base if available
            if context:
                messages.append({"role": "system", "content": f"Use this information to answer: {context}"})
            
            # Add user query
            messages.append({"role": "user", "content": user_query})
            
            # Call OpenAI API using the global client
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Error getting OpenAI response: {e}")
            
            if "insufficient_quota" in error_msg or "exceeded your current quota" in error_msg:
                return "The AI service quota has been exceeded. Please contact an administrator to update the billing plan."
            elif "authentication" in error_msg:
                return "I'm having trouble with my AI service authentication. Please ask an administrator to check the OpenAI API key."
            elif "rate limit" in error_msg:
                return "I've reached my usage limit. Please try again later or contact an administrator."
            elif "api" in error_msg:
                return "The AI service is currently experiencing issues. Please try again later."
            else:
                return "I'm having trouble connecting to my knowledge base. Please try again later."
    
    def get_response(self, user_query, user_id):
        """Get a response to the user query using hybrid approach"""
        try:
            # First try to find a similar question in the knowledge base
            similar_entry, score = self.find_similar_question(user_query)
            
            # Make sure the model is trained
            if not self.trained:
                print("Model not trained. Training now...")
                self.train()
                # Try again after training
                similar_entry, score = self.find_similar_question(user_query)
            
            if similar_entry and score > 0.7:  # High confidence match
                response = similar_entry.answer
                source = "knowledge_base"
                print(f"Found high confidence match ({score:.2f}) in knowledge base for: {user_query}")
            elif similar_entry and score > 0.5:  # Medium confidence match
                # Use the knowledge base entry as context for OpenAI
                context = f"Question: {similar_entry.question}\nAnswer: {similar_entry.answer}"
                print(f"Found medium confidence match ({score:.2f}) in knowledge base, using as context for: {user_query}")
                
                # If OpenAI client is not available, fall back to knowledge base
                if not openai_client:
                    response = similar_entry.answer
                    source = "knowledge_base_fallback"
                    print("OpenAI client not available, falling back to knowledge base answer")
                else:
                    try:
                        response = self.get_openai_response(user_query, context)
                        source = "hybrid"
                    except Exception as e:
                        print(f"OpenAI error: {e}, falling back to knowledge base")
                        response = similar_entry.answer
                        source = "knowledge_base_fallback"
            else:  # No good match in knowledge base
                print(f"No good match in knowledge base for: {user_query}")
                # If OpenAI client is not available, return a fallback message
                if not openai_client:
                    response = "I don't have specific information about that in my knowledge base. Please try asking something about university services, policies, or facilities."
                    source = "fallback"
                    print("OpenAI client not available, using fallback message")
                else:
                    try:
                        response = self.get_openai_response(user_query)
                        source = "openai"
                    except Exception as e:
                        print(f"OpenAI error: {e}, using fallback message")
                        response = "I don't have specific information about that. Please try asking something about university services, policies, or facilities."
                        source = "fallback"
            
            # Save chat history
            try:
                chat_entry = ChatHistory(
                    user_id=user_id,
                    user_message=user_query,
                    bot_response=response
                )
                db.session.add(chat_entry)
                db.session.commit()
            except Exception as e:
                print(f"Error saving chat history: {e}")
                # Continue even if saving history fails
            
            return response, source
        except Exception as e:
            print(f"Error in get_response: {e}")
            return "I'm having trouble processing your request. Please try again later.", "error"

# Create a singleton instance
ai_model = AIModel()

def initialize_model():
    """Initialize and train the AI model"""
    success = ai_model.train()
    if success:
        print("AI model successfully trained and initialized.")
    else:
        print("WARNING: AI model training failed. Chatbot may not work properly.")
    return success