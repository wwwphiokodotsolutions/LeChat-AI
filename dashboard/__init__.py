"""
DevOps Dashboard Module
Provides monitoring and management capabilities for DevOps workflows.
"""

from .app import create_app
from .monitoring import system_monitor, github_monitor, docker_monitor

__version__ = "1.0.0"
__all__ = ['create_app', 'system_monitor', 'github_monitor', 'docker_monitor']