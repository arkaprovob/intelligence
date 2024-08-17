"""
appstate package

This package manages the application state, including database connections
and shared resources across different modules of the application.

Key components:
- db_manager: Handles database connections and operations
- init_database: Initializes the database and creates necessary tables
- feedback_manager: Manages feedback-related operations

Usage:
from appstate import db_manager, init_database, feedback_manager
"""

from .database import db_manager, init_database
from .feedback.feedback_manager import feedback

__all__ = ['db_manager', 'init_database', feedback]