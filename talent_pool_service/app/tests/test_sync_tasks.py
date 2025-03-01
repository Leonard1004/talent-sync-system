import pytest
from unittest.mock import patch, MagicMock
from app.tasks.sync_tasks import sync_talent_pool_data, send_bulk_data_to_job_seeker

@patch('app.tasks.sync_tasks.SessionLocal')
@patch('app.tasks.sync_tasks.send_bulk_data_to_job_seeker')
def test_sync_talent_pool_data(mock_send_task, mock_session):
    # Create mock session and query results
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    # Mock talent pools
    mock_talent_pool = MagicMock()
    mock_talent_pool.talent_pool_id = "test-pool-1"
    mock_talent_pool.talent_pool_name = "Test Talent Pool"
    
    mock_db.query().all.return_value = [mock_talent_pool]
    
    # Mock the sync job creation
    mock_sync_job = MagicMock()
    mock_sync_job.id = "test-job-id"
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    
    # Call the function
    result = sync_talent_pool_data()
    
    # Check the results
    assert result["status"] == "success"
    assert "Scheduled sync" in result["message"]
    
    # Verify that the background task was called
    mock_send_task.delay.assert_called_once()

@patch('app.tasks.sync_tasks.SessionLocal')
@patch('app.tasks.sync_tasks.requests.post')
def test_send_bulk_data_to_job_seeker_success(mock_post, mock_session):
    # Create mock session and query results
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    # Mock sync job
    mock_sync_job = MagicMock()
    mock_sync_job.id = "test-job-id"
    mock_sync_job.status = "pending"
    mock_sync_job.data = {"profiles": []}
    mock_sync_job.retry_count = 0
    
    mock_db.query().filter().first.return_value = mock_sync_job
    
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_post.return_value = mock_response
    
    # Call the function
    send_bulk_data_to_job_seeker("test-job-id")
    
    # Verify that the API was called
    mock_post.assert_called_once()
    
    # Verify that the sync job was updated
    assert mock_sync_job.status == "success"
    mock_db.commit.assert_called_once()