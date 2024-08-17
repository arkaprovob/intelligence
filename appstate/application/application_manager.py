from typing import List, Dict, Any
from ..database import db_manager

class ApplicationManager:
    """
    Class for managing application-related database operations.

    This class provides static methods to interact with the application table in the database,
    utilizing the DatabaseManager (db_manager) for executing queries. It offers functionality to:
    - Save new application entries
    - Fetch applications with pagination
    - Search applications based on a search term
    - Delete application records based on name
    - Update application records

    All methods are implemented as static methods, allowing for easy use without instantiation.
    The class relies on the db_manager for database connections and query execution.
    """

    @staticmethod
    async def save(name: str, domain: str, tag: str, hidden: bool = False):
        await db_manager.execute('''
            INSERT INTO application (name, domain, tag, hidden)
            VALUES ($1, $2, $3, $4)
        ''', name, domain, tag, hidden)

    @staticmethod
    async def fetch(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM application
            ORDER BY name
            LIMIT $1 OFFSET $2
        """
        results = await db_manager.fetch(query, limit, offset)
        return [dict(result) for result in results]

    @staticmethod
    async def search(search_term: str) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM application
            WHERE name ILIKE $1
               OR domain ILIKE $1
               OR tag ILIKE $1
            ORDER BY name
        """
        search_pattern = f'%{search_term}%'
        results = await db_manager.fetch(query, search_pattern)
        return [dict(result) for result in results]

    @staticmethod
    async def delete(name: str):
        query = "DELETE FROM application WHERE name = $1"
        await db_manager.execute(query, name)
        print(f"Application with name '{name}' has been deleted.")

    @staticmethod
    async def update(name: str, domain: str = None, tag: str = None, hidden: bool = None):
        update_fields = []
        update_values = []
        if domain is not None:
            update_fields.append("domain = $1")
            update_values.append(domain)
        if tag is not None:
            update_fields.append(f"tag = ${len(update_values) + 1}")
            update_values.append(tag)
        if hidden is not None:
            update_fields.append(f"hidden = ${len(update_values) + 1}")
            update_values.append(hidden)

        if not update_fields:
            print("No fields to update.")
            return

        query = f"""
            UPDATE application
            SET {', '.join(update_fields)}
            WHERE name = ${len(update_values) + 1}
        """
        update_values.append(name)
        await db_manager.execute(query, *update_values)
        print(f"Application '{name}' has been updated.")

application = ApplicationManager()