from typing import List, Dict, Any
from ..database import db_manager

class FeedbackManager:

    """
    class for managing feedback-related database operations.

    This class provides static methods to interact with the feedback table in the database,
    utilizing the DatabaseManager (db_manager) for executing queries. It offers functionality to:
    - Save new feedback entries
    - Fetch feedback with pagination
    - Search feedback based on a search term
    - Delete feedback records based on conditions

    All methods are implemented as static methods, allowing for easy use without instantiation.
    The class relies on the db_manager for database connections and query execution.
    """

    @staticmethod
    async def save(user_question: str, answer: str = "none", feedback: int = 0, user: str = "anonymous",
                            description: str = "none"):
        await db_manager.execute('''
            INSERT INTO feedback (answer, feedback, user_question, user_id, description)
            VALUES ($1, $2, $3, $4, $5)
        ''', answer, feedback, user_question, user, description)

    @staticmethod
    async def fetch(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM feedback
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        results = await db_manager.fetch(query, limit, offset)
        return [dict(result) for result in results]

    @staticmethod
    async def search(search_term: str) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM feedback
            WHERE answer ILIKE $1
               OR user_question ILIKE $1
               OR description ILIKE $1
            ORDER BY created_at DESC
        """
        search_pattern = f'%{search_term}%'
        results = await db_manager.fetch(query, search_pattern)
        return [dict(result) for result in results]

    @staticmethod
    async def delete(conditions: Dict[str, Any] = None):
        if conditions is None:
            await db_manager.execute("DELETE FROM feedback")
            print("All records deleted from the feedback table.")
        else:
            where_clause = " AND ".join([f"{key} = ${i + 1}" for i, key in enumerate(conditions.keys())])
            query = f"DELETE FROM feedback WHERE {where_clause}"
            await db_manager.execute(query, *conditions.values())
            print(f"Records matching the conditions {conditions} have been deleted.")

feedback = FeedbackManager()