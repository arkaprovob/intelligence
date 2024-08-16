import logging
import os
from typing import List, Dict, Any

import asyncpg
from contextlib import asynccontextmanager

from util import get_config_value


class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.DB_HOST = get_config_value("PG_HOST")
        self.DB_PORT = get_config_value("PG_PORT")
        self.DB_NAME = get_config_value("PG_NAME")
        self.DB_USER = get_config_value("PG_USER")
        self.DB_PASSWORD = get_config_value("PG_PASSWORD")
        self.DEFAULT_PG_DATABASE = get_config_value("PG_DEFAULT_DATABASE")

    async def create_db_if_not_exists(self):
        # Connect to 'postgres' database to create a new database
        sys_conn = await asyncpg.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DEFAULT_PG_DATABASE
        )

        try:
            # Check if the database exists
            exists = await sys_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", self.DB_NAME
            )

            if not exists:
                # Database doesn't exist, so create it
                await sys_conn.execute(f"CREATE DATABASE {self.DB_NAME}")
                print(f"Database {self.DB_NAME} created successfully")
            else:
                print(f"Database {self.DB_NAME} already exists")
        finally:
            await sys_conn.close()

    async def initialize(self):
        await self.create_db_if_not_exists()
        self.pool = await asyncpg.create_pool(
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            min_size=1,
            max_size=10
        )

    async def kickoff(self):
        try:
            await self.initialize()
            await self.init_db()
        except Exception as e:
            print(f"Error during kickoff: {str(e)}")
            logging.debug("Traceback:", exc_info=True)

    async def close(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self):
        if self.pool is None:
            await self.initialize()
        async with self.pool.acquire() as connection:
            yield connection

    async def init_db(self):
        await self.initialize()  # This will create the database if it doesn't exist
        async with self.get_connection() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    answer TEXT NOT NULL,
                    feedback INTEGER NOT NULL,
                    user_question TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    async def save_feedback(self, user_question: str, answer: str = "none", feedback: int = 0, user: str = "anonymous",
                            description: str = "none"):
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO feedback (answer, feedback, user_question, user_id, description)
                VALUES ($1, $2, $3, $4, $5)
            ''', answer, feedback, user_question, user, description)

    async def fetch_records(self, query: str, *args) -> List[Dict[str, Any]]:
        """
        executes a query and returns the results as a list of dictionaries.

        :param query: SQL query string
        :param args: Optional arguments for the SQL query
        :return: List of dictionaries, where each dictionary represents a row
        """
        async with self.get_connection() as conn:
            results = await conn.fetch(query, *args)
            return [dict(result) for result in results]

    async def fetch_feedback(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        fwetches feedback records with pagination.

        :param limit: Maximum number of records to return (default 100)
        :param offset: Number of records to skip (default 0)
        :return: List of dictionaries, where each dictionary represents a feedback record
        """
        query = """
            SELECT * FROM feedback
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        return await self.fetch_records(query, limit, offset)

    async def search_feedback(self, search_term: str) -> List[Dict[str, Any]]:
        """
        searches for feedback records containing the given search term.

        :param search_term: Term to search for in answer, user_question, or description
        :return: List of dictionaries, where each dictionary represents a matching feedback record
        """
        query = """
            SELECT * FROM feedback
            WHERE answer ILIKE $1
               OR user_question ILIKE $1
               OR description ILIKE $1
            ORDER BY created_at DESC
        """
        search_pattern = f'%{search_term}%'
        return await self.fetch_records(query, search_pattern)

    async def delete_records(self, conditions: Dict[str, Any] = None):
        """
        deletes records from the feedback table.
        if no conditions are provided, all records are deleted.
        Otherwise, records matching the provided conditions are deleted.

        :param conditions: Optional dictionary of column-value pairs for conditional deletion
        """
        async with self.get_connection() as conn:
            if conditions is None:
                # Delete all records
                await conn.execute("DELETE FROM feedback")
                print("All records deleted from the feedback table.")
            else:
                # Construct the WHERE clause based on the conditions
                where_clause = " AND ".join([f"{key} = ${i + 1}" for i, key in enumerate(conditions.keys())])
                query = f"DELETE FROM feedback WHERE {where_clause}"

                # Execute the delete query with the condition values
                await conn.execute(query, *conditions.values())
                print(f"Records matching the conditions {conditions} have been deleted.")
