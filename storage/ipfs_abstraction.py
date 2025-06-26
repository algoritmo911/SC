# storage/ipfs_abstraction.py
import httpx # Using httpx for async requests, can also use aioipfs or other IPFS client libraries
from typing import Any, Dict, Optional #, AsyncGenerator

# Assuming KnowledgeUnit and StorageInterface are defined in core
# from core.interfaces import StorageInterface
# from core.knowledge_units import KnowledgeUnit # If needed directly, though interface is preferred

# Placeholder for the actual StorageInterface from core.interfaces
# This is to avoid circular dependencies if this file is type-checked standalone.
# In a real setup, you'd import it: from core.interfaces import StorageInterface
class StorageInterface: # Placeholder
    async def store_knowledge_unit_content(self, content: bytes) -> str: pass
    async def retrieve_knowledge_unit_content(self, content_address: str) -> bytes: pass
    async def store_metadata(self, metadata: Dict[str, Any], metadata_id: Optional[str] = None) -> str: pass
    async def retrieve_metadata(self, metadata_id: str) -> Optional[Dict[str, Any]]: pass
    async def store_knowledge_unit_object(self, ku: Any) -> str: pass # ku would be KnowledgeUnit
    async def retrieve_knowledge_unit_object(self, ku_id: str) -> Optional[Any]: pass # ku would be KnowledgeUnit


class IPFSStorage(StorageInterface):
    """
    Implementation of StorageInterface using an IPFS daemon via its HTTP API.
    Requires an IPFS daemon to be running and accessible.
    """
    def __init__(self, ipfs_api_base_url: str = "http://127.0.0.1:5001/api/v0"):
        """
        Initializes the IPFSStorage client.
        Args:
            ipfs_api_base_url: The base URL for the IPFS HTTP API.
                               Defaults to "http://127.0.0.1:5001/api/v0".
        """
        self.base_url = ipfs_api_base_url
        # It's good practice to use a persistent client session
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        # TODO: Add error handling for IPFS daemon not being available

    async def _make_request(self, endpoint: str, method: str = "POST", params: Optional[Dict] = None, files: Optional[Dict] = None, data: Optional[Dict]=None) -> Dict:
        """Helper to make requests to the IPFS API."""
        try:
            if method.upper() == "POST":
                response = await self._client.post(endpoint, params=params, files=files, data=data)
            elif method.upper() == "GET": # Primarily for cat, not typically used for add
                response = await self._client.get(endpoint, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            # For commands like 'add' that return newline-delimited JSON,
            # we might need to parse it line by line if there are multiple files.
            # For a single file, it's usually a single JSON object.
            # IPFS API often returns NDJSON, but for single file 'add' it's one line.
            # For simplicity, assuming single JSON object response for add/object put.
            # If handling multiple files in one go, this needs adjustment.
            text_response = response.text
            if text_response:
                # Attempt to parse, assuming it's a single JSON object potentially on one line
                try:
                    return json.loads(text_response)
                except json.JSONDecodeError as e:
                    # Handle cases where it might be NDJSON or plain text for some commands
                    print(f"Warning: Could not parse IPFS response as JSON: {text_response}, Error: {e}")
                    # For 'cat', it's raw bytes, not JSON. That's handled separately.
                    # This part is mainly for commands expected to return JSON like 'add' or 'object put'.
                    return {"Hash": text_response.strip()} # Fallback for simple hash string
            return {} # Should not happen if response has content and is 2xx

        except httpx.HTTPStatusError as e:
            print(f"IPFS API HTTP error: {e.response.status_code} - {e.response.text}")
            raise # Re-raise the exception to be handled by the caller
        except httpx.RequestError as e:
            print(f"IPFS API request error: {e}")
            raise # Re-raise

    async def store_knowledge_unit_content(self, content: bytes) -> str:
        """
        Stores raw content bytes to IPFS.
        Returns the IPFS CID (Content Identifier) of the stored content.
        """
        files = {"file": content}
        params = {"pin": "true"} # Pin the content to ensure it's not garbage collected
        try:
            response_data = await self._make_request("/add", files=files, params=params)
            cid = response_data.get("Hash")
            if not cid:
                raise ValueError("IPFS 'add' command did not return a Hash.")
            return cid
        except Exception as e:
            # Log error or handle more gracefully
            print(f"Error storing content to IPFS: {e}")
            raise # Or return a specific error indicator

    async def retrieve_knowledge_unit_content(self, content_address: str) -> bytes:
        """
        Retrieves raw content from IPFS given its CID.
        """
        params = {"arg": content_address}
        try:
            # The 'cat' command returns raw bytes, not JSON.
            async with self._client.stream("POST", "/cat", params=params) as response:
                response.raise_for_status()
                content = await response.aread()
                return content
        except httpx.HTTPStatusError as e:
            print(f"Error retrieving content {content_address} from IPFS: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404: # Or check specific IPFS error for not found
                return None # Or raise custom NotFound error
            raise
        except httpx.RequestError as e:
            print(f"Error retrieving content {content_address} from IPFS: {e}")
            raise

    async def store_metadata(self, metadata: Dict[str, Any], metadata_id: Optional[str] = None) -> str:
        """
        Stores a metadata dictionary as a JSON object on IPFS.
        `metadata_id` is not directly used by IPFS for content addressing but could be part of the metadata itself.
        Returns the IPFS CID of the stored JSON object.
        """
        import json # Standard library json
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        return await self.store_knowledge_unit_content(metadata_bytes) # Reuse content storage

    async def retrieve_metadata(self, metadata_cid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a JSON object from IPFS and parses it into a dictionary.
        """
        import json
        metadata_bytes = await self.retrieve_knowledge_unit_content(metadata_cid)
        if metadata_bytes:
            try:
                return json.loads(metadata_bytes.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f"Error decoding metadata from IPFS CID {metadata_cid}: {e}")
                return None
        return None

    async def store_knowledge_unit_object(self, ku: Any) -> str: # ku is KnowledgeUnit
        """
        Stores a representation of the KnowledgeUnit object on IPFS.
        This typically means storing its metadata (which includes content CID, author, etc.) as a JSON object.
        The KnowledgeUnit object itself might be defined in `core.knowledge_units`.
        For simplicity, assuming `ku` has a method `to_dict()` or can be serialized.
        """
        if not hasattr(ku, 'to_dict') and not isinstance(ku, dict):
             # If using Pydantic models from core.knowledge_units, they have model_dump()
            if hasattr(ku, 'model_dump'):
                ku_dict = ku.model_dump(mode='json') # pydantic v2
            else:
                raise TypeError("KnowledgeUnit object must be a dict or have a to_dict/model_dump method for IPFS storage.")
        elif hasattr(ku, 'to_dict'):
            ku_dict = ku.to_dict()
        else: # It's already a dict
            ku_dict = ku

        # The content itself (e.g., a large file) should already be stored,
        # and its CID should be part of ku_dict (e.g., ku_dict['content_cid'] or ku_dict['source_uri']).
        return await self.store_metadata(ku_dict)


    async def retrieve_knowledge_unit_object(self, ku_object_cid: str) -> Optional[Any]: # Returns KnowledgeUnit
        """
        Retrieves a KnowledgeUnit object's metadata from IPFS and reconstructs the object.
        This assumes the stored object was JSON metadata.
        Reconstruction into a specific Python class (e.g., KnowledgeUnit) would happen here.
        """
        metadata = await self.retrieve_metadata(ku_object_cid)
        if metadata:
            # If KnowledgeUnit class is available and metadata matches its fields:
            # from core.knowledge_units import KnowledgeUnit # Would cause issues if not careful with imports
            # return KnowledgeUnit(**metadata) # Or a more robust deserialization method
            return metadata # For now, just return the dict. Consumer can instantiate.
        return None

    async def close(self):
        """Closes the underlying HTTPX client. Should be called on application shutdown."""
        await self._client.aclose()

# Example usage (conceptual, requires running IPFS daemon and async context)
# async def main():
#     ipfs_storage = IPFSStorage()
#     try:
#         # Store some content
#         content_cid = await ipfs_storage.store_knowledge_unit_content(b"Hello IPFS world!")
#         print(f"Stored content, CID: {content_cid}")
#
#         # Retrieve content
#         retrieved_content = await ipfs_storage.retrieve_knowledge_unit_content(content_cid)
#         print(f"Retrieved content: {retrieved_content.decode()}")
#
#         # Store metadata
#         metadata = {"title": "My KU", "author": "Jules", "content_cid": content_cid}
#         metadata_cid = await ipfs_storage.store_metadata(metadata)
#         print(f"Stored metadata, CID: {metadata_cid}")
#
#         # Retrieve metadata
#         retrieved_metadata = await ipfs_storage.retrieve_metadata(metadata_cid)
#         print(f"Retrieved metadata: {retrieved_metadata}")
#
#         # Simulate KU object (assuming KnowledgeUnit is a Pydantic model or similar)
#         class MockKU: # Placeholder for core.knowledge_units.KnowledgeUnit
#             def __init__(self, id, author_id, content_hash, metadata, source_uri, version):
#                 self.id = id; self.author_id = author_id; self.content_hash = content_hash;
#                 self.metadata = metadata; self.source_uri = source_uri; self.version = version
#             def model_dump(self, mode=None): # Simulate Pydantic's model_dump
#                 return self.__dict__
#
#         ku = MockKU(id="ku1", author_id="user1", content_hash=content_cid,
#                       metadata={"tags": ["test"]}, source_uri=f"ipfs://{content_cid}", version=1)
#         ku_object_cid = await ipfs_storage.store_knowledge_unit_object(ku)
#         print(f"Stored KU object, CID: {ku_object_cid}")
#
#         retrieved_ku_data = await ipfs_storage.retrieve_knowledge_unit_object(ku_object_cid)
#         print(f"Retrieved KU data: {retrieved_ku_data}")
#         # retrieved_ku = MockKU(**retrieved_ku_data) if retrieved_ku_data else None
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         await ipfs_storage.close()

# if __name__ == "__main__":
#     import asyncio
#     # To run this example:
#     # 1. Ensure IPFS daemon is running (ipfs daemon)
#     # 2. pip install httpx
#     # asyncio.run(main())
#     pass

# Note on json import: httpx might use its own or system's json.
# Explicitly `import json` from Python's stdlib if specific features are needed.
import json # Added for clarity, though httpx handles JSON internally too.
