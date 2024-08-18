from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from ..database import db_manager

class IngestionResponse(BaseModel):
    id: Optional[int]
    name: str
    source: str
    workspace: str
    metadata: Dict[str, Any]
    additionaldetails: Optional[Dict[str, Any]] = None

class IngestionManager:

    """
    Class for managing ingestion-related database operations.

    This class provides static methods to interact with the ingestion table in the database,
    utilizing the DatabaseManager (db_manager) for executing queries. It offers functionality to:
    - Save new ingestion entries
    - Fetch ingestions with pagination
    - Search ingestions based on a search term
    - Delete ingestion records based on id
    - Update ingestion records
    """

    @staticmethod
    def parse_json(value):
        if value is None or value == "":
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    @staticmethod
    def to_json_string(value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value)
            except (TypeError, ValueError):
                return None
        return value

    @staticmethod
    async def save(name: str, source: str, workspace: str, metadata: Dict[str, Any], additionaldetails: Optional[Dict[str, Any]] = None):
        query = '''
            INSERT INTO ingestion (name, source, workspace, metadata, additionaldetails)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        '''
        metadata_json = IngestionManager.to_json_string(metadata)
        additionaldetails_json = IngestionManager.to_json_string(additionaldetails)
        return await db_manager.fetchval(query, name, source, workspace, metadata_json, additionaldetails_json)

    @staticmethod
    async def fetch(workspace: str, limit: int = 100, offset: int = 0) -> List[IngestionResponse]:
        query = """
            SELECT * FROM ingestion WHERE workspace = $1
            ORDER BY id
            LIMIT $2 OFFSET $3
        """
        results = await db_manager.fetch(query, workspace, limit, offset)
        parsed_list = []
        for result in results:
            result_dict = dict(result)
            result_dict['metadata'] = IngestionManager.parse_json(result['metadata'])
            result_dict['additionaldetails'] = IngestionManager.parse_json(result['additionaldetails'])
            parsed_list.append(IngestionResponse(**result_dict))
        return parsed_list

    @staticmethod
    async def search(search_term: str) -> List[IngestionResponse]:
        query = """
            SELECT * FROM ingestion
            WHERE name ILIKE $1
               OR source ILIKE $1
               OR metadata::text ILIKE $1
               OR additionaldetails::text ILIKE $1
            ORDER BY id
        """
        search_pattern = f'%{search_term}%'
        results = await db_manager.fetch(query, search_pattern)
        parsed_list = []
        for result in results:
            result_dict = dict(result)
            result_dict['metadata'] = IngestionManager.parse_json(result['metadata'])
            result_dict['additionaldetails'] = IngestionManager.parse_json(result['additionaldetails'])
            parsed_list.append(IngestionResponse(**result_dict))
        return parsed_list

    @staticmethod
    async def delete(id: int):
        query = "DELETE FROM ingestion WHERE id = $1"
        await db_manager.execute(query, id)

    @staticmethod
    async def update(id: int, name: str = None, source: str = None, metadata: Dict[str, Any] = None, additionaldetails: Optional[Dict[str, Any]] = None):
        update_fields = []
        update_values = []
        if name is not None:
            update_fields.append("name = $1")
            update_values.append(name)
        if source is not None:
            update_fields.append(f"source = ${len(update_values) + 1}")
            update_values.append(source)
        if metadata is not None:
            update_fields.append(f"metadata = ${len(update_values) + 1}")
            update_values.append(IngestionManager.to_json_string(metadata))
        if additionaldetails is not None:
            update_fields.append(f"additionaldetails = ${len(update_values) + 1}")
            update_values.append(IngestionManager.to_json_string(additionaldetails))

        if not update_fields:
            return

        query = f"""
            UPDATE ingestion
            SET {', '.join(update_fields)}
            WHERE id = ${len(update_values) + 1}
        """
        update_values.append(id)
        await db_manager.execute(query, *update_values)

ingestion = IngestionManager()