from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from models import User, ChatbotKnowledge, Feedback, ChatHistory
#from forms import LoginForm, RegistrationForm, FeedbackForm, KnowledgeForm, ProfileUpdateForm
from forms import LoginForm, RegistrationForm, FeedbackForm, KnowledgeForm, ProfileUpdateForm, UserEditForm
from datetime import datetime
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to import AI model with error handling
try:
    from ai_model import ai_model, initialize_model
    ai_model_available = True
    logger.info("AI model imported successfully")
except ImportError as e:
    logger.error(f"Failed to import AI model: {e}")
    ai_model_available = False
except Exception as e:
    logger.error(f"Error importing AI model: {e}")
    ai_model_available = False

# Context processor to inject variables into all templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes (unchanged, keep as is)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Chatbot routes
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', now=datetime.now())

@app.route('/chat_api', methods=['POST'])
@login_required
def chat_api():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    logger.info(f"Received message from user {current_user.id}: {user_message}")
    
    if not user_message:
        return jsonify({
            'response': "I didn't receive a message. Please try again.",
            'source': "error"
        })
    
    # Initialize response and source
    response = "I'm sorry, I encountered an error. Please try again."
    source = "error"
    
    try:
        # First, check if we have any knowledge base entries at all
        knowledge_count = ChatbotKnowledge.query.count()
        logger.info(f"Total knowledge base entries: {knowledge_count}")
        
        # Try to find a match in the knowledge base
        # Use more flexible search
        knowledge_entry = None
        
        # Try exact match first
        knowledge_entry = ChatbotKnowledge.query.filter(
            db.func.lower(ChatbotKnowledge.question) == db.func.lower(user_message)
        ).first()
        
        if not knowledge_entry:
            # Try partial match
            knowledge_entry = ChatbotKnowledge.query.filter(
                ChatbotKnowledge.question.ilike(f'%{user_message}%')
            ).first()
        
        if knowledge_entry:
            response = knowledge_entry.answer
            source = "knowledge_base"
            logger.info(f"Found knowledge base match: {knowledge_entry.question}")
        else:
            logger.info(f"No direct match found for: {user_message}")
            
            # Use AI model if available
            if ai_model_available:
                try:
                    # Initialize model if needed
                    if hasattr(ai_model, 'is_initialized') and not ai_model.is_initialized:
                        initialize_model()
                    
                    # Get AI response
                    response, source = ai_model.get_response(user_message, current_user.id)
                    logger.info(f"AI model response received, source: {source}")
                except Exception as ai_error:
                    logger.error(f"AI model error: {ai_error}")
                    response = "I'm currently unable to process complex questions. Please try a simpler query or contact support."
                    source = "error"
            else:
                # AI model not available
                response = "The AI service is currently unavailable. Please try asking about university services, policies, or facilities."
                source = "fallback"
                
    except Exception as e:
        logger.error(f"Error in chat_api: {str(e)}", exc_info=True)
        
        # Try to provide a more helpful error message
        error_msg = str(e).lower()
        
        if "connection" in error_msg or "timeout" in error_msg:
            response = "Unable to connect to the service. Please check your internet connection and try again."
        elif "database" in error_msg or "sql" in error_msg:
            response = "Database error. Please try again later."
        else:
            response = f"I'm having trouble processing your request. Error: {str(e)[:100]}"
    
    # Save chat history
    try:
        chat_entry = ChatHistory(
            user_id=current_user.id,
            user_message=user_message,
            bot_response=response,
            source=source
        )
        db.session.add(chat_entry)
        db.session.commit()
        logger.info(f"Chat history saved for user {current_user.id}")
    except Exception as db_error:
        logger.error(f"Error saving chat history: {db_error}")
        # Don't fail if we can't save history
    
    logger.info(f"Sending response: {response[:50]}... (source: {source})")
    
    return jsonify({
        'response': response,
        'source': source
    })

# Feedback routes (unchanged)
@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            user_id=current_user.id,
            feedback_text=form.feedback_text.data,
            rating=form.rating.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('index'))
    
    return render_template('feedback.html', form=form)

# Admin routes (unchanged)
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('admin/dashboard.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# ADDED DELETE USER ROUTE HERE
@app.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get the user to delete
    user_to_delete = User.query.get_or_404(id)
    
    # Prevent deleting yourself
    if user_to_delete.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin_users'))
    
    # Prevent deleting the last admin
    if user_to_delete.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot delete the last admin account!', 'danger')
            return redirect(url_for('admin_users'))
    
 
    @app.route('/admin/users/delete/<int:id>', methods=['POST'])
    @login_required
    def delete_user(id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
        return redirect(url_for('manage_users'))


@app.route('/admin/knowledge', methods=['GET', 'POST'])
@login_required
def admin_knowledge():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    form = KnowledgeForm()
    if form.validate_on_submit():
        knowledge = ChatbotKnowledge(
            question=form.question.data,
            answer=form.answer.data
        )
        db.session.add(knowledge)
        db.session.commit()
        flash('Knowledge base entry added successfully!', 'success')
        return redirect(url_for('admin_knowledge'))
    
    knowledge_entries = ChatbotKnowledge.query.all()
    return render_template('admin/knowledge.html', form=form, knowledge_entries=knowledge_entries)

@app.route('/admin/knowledge/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_knowledge(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    knowledge = ChatbotKnowledge.query.get_or_404(id)
    form = KnowledgeForm(obj=knowledge)
    
    if form.validate_on_submit():
        knowledge.question = form.question.data
        knowledge.answer = form.answer.data
        knowledge.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Knowledge base entry updated successfully!', 'success')
        return redirect(url_for('admin_knowledge'))
    
    return render_template('admin/edit_knowledge.html', form=form, knowledge=knowledge)

@app.route('/admin/knowledge/<int:id>/delete', methods=['POST'])
@login_required
def delete_knowledge(id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    knowledge = ChatbotKnowledge.query.get_or_404(id)
    db.session.delete(knowledge)
    db.session.commit()
    flash('Knowledge base entry deleted successfully!', 'success')
    return redirect(url_for('admin_knowledge'))

@app.route('/admin/feedback')
@login_required
def admin_feedback():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    feedback = Feedback.query.all()
    
    # Calculate average rating 
    avg_rating = 0
    if feedback:
        total_rating = sum(f.rating for f in feedback)
        avg_rating = round(total_rating / len(feedback), 1) if len(feedback) > 0 else 0
    
    # Calculate rating counts
    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = sum(1 for f in feedback if f.rating == i)
    
    return render_template('admin/feedback.html', feedback=feedback, avg_rating=avg_rating, rating_counts=rating_counts)

# Profile route (unchanged)
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm(original_username=current_user.username, original_email=current_user.email)
    
    if form.validate_on_submit():
        # Verify current password
        if check_password_hash(current_user.password, form.current_password.data):
            # Update username and email
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            # Update password if provided
            if form.new_password.data:
                current_user.password = generate_password_hash(form.new_password.data)
                
            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('profile.html', form=form)