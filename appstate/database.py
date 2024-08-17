import logging
import asyncpg
from contextlib import asynccontextmanager
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from util import get_config_value

class DatabaseManager:
    """
    class for managing asynchronous database connections and operations using asyncpg.

    This class provides functionality to:
    - Initialize and manage a connection pool
    - Create a database if it doesn't exist
    - Execute SQL queries and transactions
    - Handle connection errors and retries
    - Perform database health checks

    The class uses environment variables for configuration and implements
    retry mechanisms for improved reliability in database operations.
    """

    def __init__(self):
        self.pool = None
        self.DB_HOST = get_config_value("PG_HOST")
        self.DB_PORT = get_config_value("PG_PORT")
        self.DB_NAME = get_config_value("PG_NAME")
        self.DB_USER = get_config_value("PG_USER")
        self.DB_PASSWORD = get_config_value("PG_PASSWORD")
        self.DEFAULT_PG_DATABASE = get_config_value("PG_DEFAULT_DATABASE")

    async def create_db_if_not_exists(self):
        sys_conn = await asyncpg.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DEFAULT_PG_DATABASE
        )

        try:
            exists = await sys_conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", self.DB_NAME
            )

            if not exists:
                await sys_conn.execute(f"CREATE DATABASE {self.DB_NAME}")
                print(f"Database {self.DB_NAME} created successfully")
            else:
                print(f"Database {self.DB_NAME} already exists")
        finally:
            await sys_conn.close()

    @retry(
        retry=retry_if_exception_type((asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.InterfaceError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            min_size=1,
            max_size=10
        )

    async def initialize(self):
        await self.create_db_if_not_exists()
        await self.create_pool()


    async def close(self):
        if self.pool:
            await self.pool.close()

    @classmethod
    async def check_connection(cls, connection):
        try:
            await connection.execute('SELECT 1')
            return True
        except asyncpg.exceptions.PostgresError:
            logging.error(f"Database connection check failed: {e}")
            return False

    @asynccontextmanager
    @retry(
        retry=retry_if_exception_type((asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.InterfaceError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def get_connection(self):
        if self.pool is None:
            await self.create_pool()
        try:
            async with self.pool.acquire() as connection:
                if await self.check_connection(connection):
                    yield connection
                else:
                    # Connection is not healthy, recreate the pool
                    await self.close()
                    await self.create_pool()
                    async with self.pool.acquire() as new_connection:
                        yield new_connection
        except asyncpg.exceptions.InterfaceError:
            # This exception might be raised if the pool is closed
            await self.create_pool()
            async with self.pool.acquire() as new_connection:
                yield new_connection

    @retry(
        retry=retry_if_exception_type(asyncpg.exceptions.PostgresError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def execute_transaction(self, *queries):
        async with self.get_connection() as conn:
            async with conn.transaction():
                for query in queries:
                    await conn.execute(query)

    async def execute(self, query, *args):
        async with self.get_connection() as conn:
            await conn.execute(query, *args)

    async def fetch(self, query, *args):
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)

    async def fetchval(self, query, *args):
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)


    async def get_connection_state(self):
        if self.pool is None:
            return "Not initialized"
        elif self.pool.is_closed():
            return "Closed"
        else:
            return "Open"

    async def reset_pool(self):
        await self.close()
        await self.create_pool()
        logging.info("Database connection pool has been reset")


db_manager = DatabaseManager()

async def _init_tables():
    # Create tables for all modules
    await db_manager.execute('''
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
    # Add more table creation queries here for future modules

async def init_database():
    try:
        await db_manager.initialize()
        await _init_tables()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise