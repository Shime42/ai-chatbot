import os
import sys
from app import app, db
from models import ChatbotKnowledge
from ai_model import ai_model

def train_model_from_csv(csv_file):
    """Train the AI model with data from a CSV file"""
    import csv
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file {csv_file} not found.")
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            # Process each row and add to database
            count = 0
            for row in reader:
                if len(row) >= 2:  # Ensure we have question and answer
                    question = row[0].strip()
                    answer = row[1].strip()
                    
                    # Check if question already exists
                    existing = ChatbotKnowledge.query.filter_by(question=question).first()
                    if not existing:
                        # Add new knowledge entry
                        knowledge = ChatbotKnowledge(question=question, answer=answer)
                        db.session.add(knowledge)
                        count += 1
            
            # Commit changes to database
            db.session.commit()
            print(f"Added {count} new knowledge entries to database.")
            
            # Train the model with new data
            return ai_model.train()
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False

def main():
    """Main function to train the model"""
    with app.app_context():
        # Check if we have a CSV file as argument
        if len(sys.argv) > 1:
            csv_file = sys.argv[1]
            print(f"Training model with data from {csv_file}...")
            success = train_model_from_csv(csv_file)
        else:
            # Train with existing database data
            print("Training model with existing database data...")
            success = ai_model.train()
        
        if success:
            print("Model training completed successfully.")
        else:
            print("Model training failed. Check if you have knowledge base entries in the database.")

if __name__ == "__main__":
    main()