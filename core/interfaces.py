# core/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .knowledge_units import KnowledgeUnit # Assuming KnowledgeUnit is in the same module

class StorageInterface(ABC):
    """
    Interface for interacting with underlying storage mechanisms (e.g., IPFS, Arweave).
    """
    @abstractmethod
    async def store_knowledge_unit_content(self, content: bytes) -> str:
        """
        Stores the raw content of a knowledge unit.
        Returns a unique identifier or content address (e.g., IPFS CID).
        """
        pass

    @abstractmethod
    async def retrieve_knowledge_unit_content(self, content_address: str) -> bytes:
        """
        Retrieves the raw content of a knowledge unit given its address.
        """
        pass

    @abstractmethod
    async def store_metadata(self, metadata: Dict[str, Any], metadata_id: Optional[str] = None) -> str:
        """
        Stores metadata associated with a knowledge unit or other entities.
        Returns a unique identifier for the stored metadata.
        """
        pass

    @abstractmethod
    async def retrieve_metadata(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves metadata given its identifier.
        """
        pass

    @abstractmethod
    async def store_knowledge_unit_object(self, ku: KnowledgeUnit) -> str:
        """
        Stores the complete KnowledgeUnit object (or its representation).
        This might involve storing its metadata and linking to its content.
        Returns an identifier for the stored KU object.
        """
        pass

    @abstractmethod
    async def retrieve_knowledge_unit_object(self, ku_id: str) -> Optional[KnowledgeUnit]:
        """
        Retrieves a KnowledgeUnit object by its ID.
        """
        pass


class TokenizationInterface(ABC):
    """
    Interface for interacting with tokenization mechanisms (e.g., ERC-721, ERC-20).
    """
    @abstractmethod
    async def mint_sc_tokens(self, recipient_address: str, amount: float, ku_id: str) -> str:
        """
        Mints SC (value) tokens for a contribution (KU).
        Returns a transaction hash or identifier.
        """
        pass

    @abstractmethod
    async def mint_ku_nft(self, owner_address: str, ku: KnowledgeUnit, token_uri: str) -> str:
        """
        Mints an NFT representing ownership or access to a Knowledge Unit.
        token_uri typically points to metadata about the KU (which might include its content_address).
        Returns a transaction hash or identifier for the minted NFT.
        """
        pass

    @abstractmethod
    async def transfer_sc_tokens(self, from_address: str, to_address: str, amount: float) -> str:
        """
        Transfers SC tokens between addresses.
        Returns a transaction hash or identifier.
        """
        pass

    @abstractmethod
    async def get_sc_balance(self, address: str) -> float:
        """
        Retrieves the SC token balance for a given address.
        """
        pass

    @abstractmethod
    async def get_ku_nft_owner(self, token_id: str) -> Optional[str]:
        """
        Retrieves the owner of a KU NFT.
        """
        pass

# Implementations of these interfaces will reside in the 'storage' and 'contracts' modules.
