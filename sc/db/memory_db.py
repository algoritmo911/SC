from typing import Dict, List, Optional
from ..models import KnowledgeUnit

# In-memory storage for KnowledgeUnits
# NOTE: This is for initial development and testing.
# A persistent database will be needed for production.
_knowledge_units_store: Dict[str, KnowledgeUnit] = {}

def save_knowledge_unit(ku: KnowledgeUnit) -> KnowledgeUnit:
    """Saves a KnowledgeUnit to the in-memory store."""
    _knowledge_units_store[ku.id] = ku
    return ku

def get_knowledge_unit_by_id(ku_id: str) -> Optional[KnowledgeUnit]:
    """Retrieves a KnowledgeUnit by its ID from the in-memory store."""
    return _knowledge_units_store.get(ku_id)

def get_all_knowledge_units() -> List[KnowledgeUnit]:
    """Retrieves all KnowledgeUnits from the in-memory store."""
    return list(_knowledge_units_store.values())

def clear_all_knowledge_units():
    """Clears all KnowledgeUnits from the store (useful for testing)."""
    _knowledge_units_store.clear()
