"""
Dashboard Configuration
Centralized configuration for the DevOps Dashboard
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('DASHBOARD_SECRET_KEY', 'devops-dashboard-secret-key-2024')
    DEBUG = os.getenv('DASHBOARD_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    PORT = int(os.getenv('DASHBOARD_PORT', '5000'))
    
    # Socket.IO Configuration
    SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', 'redis://')
    
    # GitHub Integration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    GITHUB_REPO = os.getenv('GITHUB_REPO', 'wwwphiokodotsolutions/LeChat-AI')
    GITHUB_POLL_INTERVAL = int(os.getenv('GITHUB_POLL_INTERVAL', '300'))  # 5 minutes
    
    # Monitoring Configuration
    MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # 1 minute
    ALERT_THRESHOLD_CPU = float(os.getenv('ALERT_THRESHOLD_CPU', '80.0'))
    ALERT_THRESHOLD_MEMORY = float(os.getenv('ALERT_THRESHOLD_MEMORY', '85.0'))
    ALERT_THRESHOLD_DISK = float(os.getenv('ALERT_THRESHOLD_DISK', '90.0'))
    
    # Docker Configuration
    DOCKER_ENABLED = os.getenv('DOCKER_ENABLED', 'True').lower() == 'true'
    DOCKER_SOCKET = os.getenv('DOCKER_SOCKET', 'unix:///var/run/docker.sock')
    
    # Database Configuration (for future use)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dashboard.db')
    
    # Security Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
    
    # Theme Configuration
    DASHBOARD_TITLE = os.getenv('DASHBOARD_TITLE', 'LeChat AI DevOps Dashboard')
    THEME_COLOR = os.getenv('THEME_COLOR', '#2563eb')
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls()

# Create configuration instance
config = Config.from_env()

if __name__ == '__main__':
    print("Dashboard Configuration:")
    for key, value in config.__dict__.items():
        if not key.startswith('_'):
            print(f"  {key}: {value}")