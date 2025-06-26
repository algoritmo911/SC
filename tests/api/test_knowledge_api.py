import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient # For async client if needed, TestClient handles it for FastAPI
import io
import os

# Adjust the import path according to your project structure
# This assumes your tests directory is at the root level, parallel to 'sc'
from sc.main import app  # Import your FastAPI app
from sc.models import KnowledgeUnit, ModerationStatus # Import your models
from sc.db import memory_db # To help with cleanup or assertions if needed

# Use TestClient for sending requests to your FastAPI app
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db_before_each_test():
    """Fixture to clear the in-memory database before each test."""
    memory_db.clear_all_knowledge_units()
    yield # This is where the test runs

def test_upload_vr_scene_success():
    """Test successful VR scene upload."""
    # Create a dummy file for upload
    dummy_file_content = b"This is a dummy VR scene file."
    dummy_file = io.BytesIO(dummy_file_content)
    dummy_file.name = "test_vr_scene.gltf" # httpx/fastapi needs a name for UploadFile

    response = client.post(
        "/api/knowledge/upload_vr",
        files={"vr_scene": (dummy_file.name, dummy_file, "model/gltf+json")},
        data={
            "content_text": "My first VR experience",
            "tags": ["test", "vr"]
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data
    assert "ipfs_hash" in data
    assert data["vr_scene_url"].startswith("ipfs://")

    # Verify it's in the mock DB
    ku_id = data["id"]
    stored_ku = memory_db.get_knowledge_unit_by_id(ku_id)
    assert stored_ku is not None
    assert stored_ku.content_text == "My first VR experience"
    assert stored_ku.author_id == "mock_author_123" # From the mocked JWT function
    assert "test" in stored_ku.tags
    assert "vr" in stored_ku.tags
    assert stored_ku.vr_scene_url == data["vr_scene_url"]

def test_upload_vr_scene_no_file():
    """Test uploading without a VR scene file."""
    # FastAPI/Starlette's TestClient will raise an error if a required File(...) is not provided.
    # The validation happens before the endpoint logic in this case.
    # To test this properly, we'd need to construct a multipart request that omits the file part.
    # However, typically the client or framework handles this.
    # For now, let's test the behavior if the endpoint logic were to receive a None file,
    # though FastAPI's File(...) makes this less likely for `vr_scene`.

    # If `File(...)` is used, Starlette/FastAPI handles the 422 Unprocessable Entity response.
    # We can check for that.
    response = client.post(
        "/api/knowledge/upload_vr",
        # No 'files' part
        data={
            "content_text": "Missing file test",
            "tags": ["fail"]
        }
    )
    # Expecting a 422 because the "vr_scene" file part is missing
    assert response.status_code == 422
    assert "detail" in response.json()
    # Example detail: [{'type': 'missing', 'loc': ['body', 'vr_scene'], 'msg': 'Field required', ...}]


def test_upload_vr_scene_no_content_text():
    """Test uploading without content_text."""
    dummy_file_content = b"dummy data"
    dummy_file = io.BytesIO(dummy_file_content)
    dummy_file.name = "test.gltf"

    response = client.post(
        "/api/knowledge/upload_vr",
        files={"vr_scene": (dummy_file.name, dummy_file, "model/gltf+json")},
        data={
            # "content_text": "This is missing", # content_text is required by Form(...)
            "tags": ["fail"]
        }
    )
    assert response.status_code == 422 # Unprocessable Entity
    data = response.json()
    assert "detail" in data
    # Check that the error message indicates 'content_text' is missing
    found_content_text_error = False
    for error in data.get("detail", []):
        if error.get("loc") and "content_text" in error["loc"]:
            found_content_text_error = True
            break
    assert found_content_text_error


def test_get_knowledge_unit_success():
    """Test retrieving a specific Knowledge Unit."""
    # First, create one
    ku = KnowledgeUnit(
        author_id="test_author",
        content_text="Test KU for retrieval",
        vr_scene_url="ipfs://testhash_retrieve"
    )
    memory_db.save_knowledge_unit(ku)

    response = client.get(f"/api/knowledge/{ku.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == ku.id
    assert data["content_text"] == "Test KU for retrieval"
    assert data["vr_scene_url"] == "ipfs://testhash_retrieve"

def test_get_knowledge_unit_not_found():
    """Test retrieving a non-existent Knowledge Unit."""
    response = client.get("/api/knowledge/non_existent_id_123")
    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge Unit not found"

def test_list_knowledge_units_empty():
    """Test listing Knowledge Units when none exist."""
    response = client.get("/api/knowledge")
    assert response.status_code == 200
    assert response.json() == []

def test_list_knowledge_units_with_data():
    """Test listing Knowledge Units when some exist."""
    ku1 = KnowledgeUnit(author_id="author1", content_text="KU1")
    ku2 = KnowledgeUnit(author_id="author2", content_text="KU2", vr_scene_url="ipfs://hash2")
    memory_db.save_knowledge_unit(ku1)
    memory_db.save_knowledge_unit(ku2)

    response = client.get("/api/knowledge")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Check if IDs are present (order might vary)
    response_ids = {item["id"] for item in data}
    assert ku1.id in response_ids
    assert ku2.id in response_ids

    # Verify content by checking one of them
    if data[0]["id"] == ku1.id:
        assert data[0]["content_text"] == "KU1"
        assert data[1]["content_text"] == "KU2"
    else:
        assert data[0]["content_text"] == "KU2"
        assert data[1]["content_text"] == "KU1"

# Example of how you might test tags being optional
def test_upload_vr_scene_no_tags():
    """Test successful VR scene upload without providing tags."""
    dummy_file_content = b"This is another dummy VR scene file."
    dummy_file = io.BytesIO(dummy_file_content)
    dummy_file.name = "test_vr_scene_no_tags.gltf"

    response = client.post(
        "/api/knowledge/upload_vr",
        files={"vr_scene": (dummy_file.name, dummy_file, "model/gltf+json")},
        data={
            "content_text": "VR scene without tags"
            # Tags are omitted, should default to empty list
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"

    ku_id = data["id"]
    stored_ku = memory_db.get_knowledge_unit_by_id(ku_id)
    assert stored_ku is not None
    assert stored_ku.tags == [] # Should be an empty list by model default or endpoint logic
    assert stored_ku.content_text == "VR scene without tags"
