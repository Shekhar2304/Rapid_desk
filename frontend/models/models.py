from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

# ✅ FIXED: Use IST timezone globally for ALL models
IST = pytz.timezone('Asia/Kolkata')

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), 
                          onupdate=lambda: datetime.now(IST), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # ✅ FIXED: SAFE CASCADE - No delete cascade to prevent IntegrityError
    tickets = db.relationship('Ticket', 
                            back_populates='user', 
                            lazy='dynamic',
                            cascade='save-update, merge')  # 🚫 NO delete/delete-orphan
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    priority = db.Column(db.String(20), nullable=False, index=True)
    status = db.Column(db.String(20), default='open', index=True)
    ai_category = db.Column(db.String(50))
    ai_priority = db.Column(db.String(20))
    ai_confidence = db.Column(db.Float)
    ai_insights = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), 
                          nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), 
                          onupdate=lambda: datetime.now(IST), index=True)
    
    # ✅ FIXED: Proper bidirectional relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user = db.relationship('User', back_populates='tickets', lazy='joined')
    
    # ✅ FIXED: History cascade - SAFE for ticket deletion
    history = db.relationship('TicketHistory', 
                            back_populates='ticket', 
                            lazy='dynamic',
                            cascade='all, delete-orphan',  # ✅ Safe for ticket history
                            order_by='desc(TicketHistory.created_at)')
    
    def display_user(self):
        """Safe user display - prevents None errors"""
        return self.user.username if self.user else 'SYSTEM'

class TicketHistory(db.Model):
    __tablename__ = 'ticket_history'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    
    # ✅ Foreign key properly references Ticket.id
    ticket = db.relationship('Ticket', 
                           back_populates='history', 
                           lazy='joined')
    
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    changed_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), 
                          nullable=False, index=True)

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    company = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), 
                          nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)

# 🚀 UTILITY FUNCTIONS FOR SAFE OPERATIONS
def reassign_user_tickets(old_user_id, new_user_id):
    """Safely reassign all tickets from one user to another"""
    tickets = Ticket.query.filter_by(user_id=old_user_id).all()
    for ticket in tickets:
        ticket.user_id = new_user_id
    return len(tickets)

def fix_orphaned_tickets(admin_user_id):
    """Fix any tickets with NULL user_id"""
    orphaned = Ticket.query.filter(Ticket.user_id.is_(None)).all()
    fixed_count = 0
    for ticket in orphaned:
        ticket.user_id = admin_user_id
        fixed_count += 1
    return fixed_count
