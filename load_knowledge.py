import os
import sys
import csv
from app import app, db
from models import ChatbotKnowledge
from train_model import train_model_from_csv
from ai_model import ai_model

def verify_knowledge_database():
    """Verify if the knowledge database has entries and load from CSV if empty"""
    with app.app_context():
        try:
            # Check if knowledge database is empty
            knowledge_count = ChatbotKnowledge.query.count()
            print(f"Current knowledge database entries: {knowledge_count}")
            
            if knowledge_count == 0:
                print("Knowledge database is empty. Loading from sample_knowledge.csv...")
                csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_knowledge.csv')
                
                if not os.path.exists(csv_file):
                    print(f"Error: Sample knowledge file not found at {csv_file}")
                    return False
                
                # Verify CSV file content before loading
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader)
                        if len(header) < 2 or header[0].lower() != 'question' or header[1].lower() != 'answer':
                            print(f"Error: CSV file has invalid format. Expected headers: question,answer")
                            return False
                        
                        # Count rows to verify content
                        row_count = sum(1 for row in reader if len(row) >= 2)
                        print(f"Found {row_count} valid entries in {csv_file}")
                        
                        if row_count == 0:
                            print("Error: No valid entries found in CSV file")
                            return False
                except Exception as e:
                    print(f"Error reading CSV file: {e}")
                    return False
                
                # Load the knowledge base
                success = train_model_from_csv(csv_file)
                if success:
                    # Verify the knowledge was loaded
                    new_count = ChatbotKnowledge.query.count()
                    print(f"Successfully loaded knowledge database. New entry count: {new_count}")
                    
                    # Ensure the AI model is trained with the new data
                    if ai_model.train():
                        print("Successfully trained AI model with the loaded knowledge.")
                        return True
                    else:
                        print("Warning: Failed to train AI model with the loaded knowledge.")
                        return False
                else:
                    print("Failed to load knowledge database.")
                    return False
            else:
                print(f"Knowledge database already has {knowledge_count} entries.")
                
                # Ensure the AI model is trained with the existing data
                if not ai_model.trained:
                    print("Training AI model with existing knowledge...")
                    if ai_model.train():
                        print("Successfully trained AI model.")
                    else:
                        print("Warning: Failed to train AI model.")
                else:
                    print("AI model is already trained.")
                
                return True
        except Exception as e:
            print(f"Error verifying knowledge database: {e}")
            return False

if __name__ == "__main__":
    verify_knowledge_database()