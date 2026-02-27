import os
from datetime import timedelta


class Config:
    """🚀 Flask AI Ticket System - Complete Production Configuration"""
    
    # 🔐 Security (CRITICAL for flash messages + sessions)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ai-ticket-system-v2-2026-feb26-secure-prod-key-change-this'
    
    # 🗄️ Database (SQLite optimized for production)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aitickets_production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Prevents stale connections
        'pool_recycle': 3600,   # Recycle connections hourly
    }
    
    # 🔐 Session Management (CRITICAL for flash persistence)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)  # 24hr sessions
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 🚀 App Settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # 📧 Mail (for production email notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # 👥 Admin settings
    ADMIN_EMAIL = 'admin@aitickets.com'
    ADMIN_PASSWORD = 'admin123'


class DevelopmentConfig(Config):
    """🐛 Development - Flash messages + Debug ON"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set True for SQL debugging
    TESTING = True
    SECRET_KEY = 'dev-ai-tickets-2026-debug-flash-messages-enabled'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Short for dev
    SQLALCHEMY_DATABASE_URI = 'sqlite:///aitickets_dev.db'


class ProductionConfig(Config):
    """🔒 Production - Flash messages + Security MAX"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False
    
    # Enhanced security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)  # 30 days
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aitickets_production.db'


class TestingConfig(Config):
    """🧪 Testing config"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=60)


# 🎯 EXPORT CONFIG OBJECTS
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# 🚀 UTILITY FUNCTIONS
def init_config(app):
    """Initialize app with proper config"""
    env = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))
    print(f"✅ Config loaded: {env} | DB: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"✅ Flash messages enabled | Session lifetime: {app.config['PERMANENT_SESSION_LIFETIME']}")
