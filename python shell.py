from app import app, db
from models import User

with app.app_context():
   user = User.query.filter_by(username='your_username').first()
   user.role = 'admin'
   db.session.commit()
   

