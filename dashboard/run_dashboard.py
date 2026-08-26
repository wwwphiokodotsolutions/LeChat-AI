#!/usr/bin/env python3
"""
Run script for DevOps Dashboard
This script starts the Flask application with proper configuration
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app import create_app
from config import config

def main():
    """Main function to run the dashboard"""
    
    # Create the Flask app
    app = create_app()
    
    # Print startup information
    print("=" * 60)
    print(f"Starting {config.DASHBOARD_TITLE}")
    print("=" * 60)
    print(f"Version: 1.0.0")
    print(f"Environment: {'Development' if config.DEBUG else 'Production'}")
    print(f"Host: {config.HOST}")
    print(f"Port: {config.PORT}")
    print(f"Debug: {config.DEBUG}")
    print(f"GitHub Repository: {config.GITHUB_REPO}")
    print(f"Docker Monitoring: {'Enabled' if config.DOCKER_ENABLED else 'Disabled'}")
    print(f"Monitoring Interval: {config.MONITORING_INTERVAL}s")
    print("=" * 60)
    print("\nDashboard is starting...")
    print("Open your browser and navigate to: http://localhost:" + str(config.PORT))
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the application
    try:
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nDashboard stopped by user")
    except Exception as e:
        print(f"\n\nError starting dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()