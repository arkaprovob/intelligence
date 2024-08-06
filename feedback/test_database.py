import pytest
from feedback import DatabaseManager


@pytest.fixture(scope="module")
async def db_manager():
    manager = DatabaseManager()
    await manager.kickoff()  # Ensure the database and table are created
    try:
        yield manager
    finally:
        await manager.close()


@pytest.mark.asyncio
async def test_fetch_feedback(db_manager):
    manager = await anext(db_manager)  # Get the DatabaseManager instance

    # First, let's insert some test data
    await manager.save_feedback(
        answer="Test answer",
        feedback=1,
        user_question="Test question",
        user="test_user",
        description="Test description"
    )
    try:
        # Now fetch the feedback
        results = await manager.fetch_feedback(limit=10, offset=0)

        assert isinstance(results, list)
        assert len(results) > 0  # We should have at least the one we just inserted
        assert len(results) <= 10  # Check if the limit is respected

        for item in results:
            print(item)
            assert isinstance(item, dict)
            assert 'answer' in item
            assert 'user_question' in item
            assert 'description' in item
    finally:
        await manager.delete_records({"id": 15})


@pytest.mark.asyncio
async def test_search_feedback(db_manager):
    manager = await anext(db_manager)  # Get the DatabaseManager instance

    # Insert test data if not already present
    await manager.save_feedback(
        answer="Unique test answer",
        feedback=1,
        user_question="Unique test question",
        user="test_user",
        description="Unique test description"
    )
    try:
        # Search for the unique term
        results = await manager.search_feedback("Unique test")

        assert isinstance(results, list)
        assert len(results) > 0
        assert any("Unique test answer" in item['answer'] for item in results)
    finally:
        await manager.delete_records()


@pytest.mark.asyncio
async def test_records_feedback(db_manager):
    manager = await anext(db_manager)
    results = await manager.fetch_feedback()
    for item in results:
        print(item)
