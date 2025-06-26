from abc import ABC, abstractmethod
from typing import Any, Dict
import json
import hashlib

class IPFSAdapter(ABC):
    @abstractmethod
    def save_data(self, data: Any) -> str:
        """Saves data to IPFS and returns the content identifier (CID)."""
        pass

    @abstractmethod
    def get_data(self, cid: str) -> Any:
        """Retrieves data from IPFS using its CID."""
        pass

class MockIPFSAdapter(IPFSAdapter):
    """
    A mock implementation of the IPFSAdapter for local testing and development.
    This does not actually connect to an IPFS network but simulates its behavior.
    """
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        print("MockIPFSAdapter initialized. Data will be stored in-memory.")

    def save_data(self, data: Any) -> str:
        """
        Simulates saving data to IPFS.
        The data is serialized to JSON, then hashed to create a pseudo-CID.
        """
        try:
            # Ensure data is serializable (e.g., for KnowledgeUnit, you might need a to_dict() method)
            if hasattr(data, 'to_dict'):
                data_to_store = data.to_dict()
            elif isinstance(data, (dict, list, str, int, float, bool)):
                data_to_store = data
            else:
                # Attempt to convert to string as a fallback
                data_to_store = str(data)

            serialized_data = json.dumps(data_to_store, sort_keys=True)
            # Create a simple hash-based CID (not a real IPFS CID)
            cid = "mock_ipfs_" + hashlib.sha256(serialized_data.encode('utf-8')).hexdigest()

            self._storage[cid] = serialized_data
            print(f"MockIPFSAdapter: Saved data with CID: {cid}")
            return cid
        except TypeError as e:
            print(f"Error serializing data for MockIPFSAdapter: {e}")
            raise ValueError("Data is not JSON serializable for MockIPFSAdapter") from e

    def get_data(self, cid: str) -> Any:
        """
        Simulates retrieving data from IPFS using its pseudo-CID.
        """
        if cid not in self._storage:
            print(f"MockIPFSAdapter: CID not found: {cid}")
            return None # Or raise an error, e.g., FileNotFoundError

        serialized_data = self._storage[cid]
        print(f"MockIPFSAdapter: Retrieved data for CID: {cid}")
        try:
            return json.loads(serialized_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data from MockIPFSAdapter for CID {cid}: {e}")
            # Fallback to returning raw data if it wasn't valid JSON (shouldn't happen with current save_data)
            return serialized_data

# Example Usage (can be removed or kept for testing):
if __name__ == '__main__':
    # This example assumes core.knowledge.KnowledgeUnit has a to_dict method
    # For standalone testing, we can define a simple mock
    class MockKnowledgeUnit:
        def __init__(self, id, content):
            self.id = id
            self.content = content
        def to_dict(self):
            return {"id": self.id, "content": self.content}

    ipfs_adapter = MockIPFSAdapter()

    # Test with a dictionary
    data1 = {"message": "Hello IPFS"}
    cid1 = ipfs_adapter.save_data(data1)
    retrieved_data1 = ipfs_adapter.get_data(cid1)
    print(f"Original: {data1}, Retrieved: {retrieved_data1}")
    assert data1 == retrieved_data1

    # Test with a mock object that has to_dict
    knowledge_content = MockKnowledgeUnit(id="ku123", content="This is some knowledge.")
    cid2 = ipfs_adapter.save_data(knowledge_content)
    retrieved_data2 = ipfs_adapter.get_data(cid2)
    print(f"Original KU: {knowledge_content.to_dict()}, Retrieved KU: {retrieved_data2}")
    assert knowledge_content.to_dict() == retrieved_data2

    # Test getting non-existent CID
    non_existent_data = ipfs_adapter.get_data("non_existent_cid")
    assert non_existent_data is None
    print("MockIPFSAdapter example usage complete.")
