"""
appstate package

This package manages the application state, including database connections
and shared resources across different modules of the application.

Key components:
- db_manager: Handles database connections and operations
- init_database: Initializes the database and creates necessary tables
- feedback_manager: Manages feedback-related operations
- application_manager: Manages application-related operations

Usage:
from appstate import db_manager, init_database, feedback, application
"""

from .database import db_manager, init_database
from .feedback.feedback_manager import feedback
from .application.application_manager import application

__all__ = ['db_manager', 'init_database', 'feedback', 'application']