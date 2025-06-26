# core/knowledge_units.py
from typing import List, Dict, Any
from dataclasses import dataclass, field
import uuid

@dataclass
class KnowledgeUnit:
    """
    Represents an intellectual unit (Knowledge Unit - KU) within the system.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    content_hash: str  # Hash of the content, for integrity and uniqueness
    metadata: Dict[str, Any] = field(default_factory=dict) # e.g., title, tags, creation_date
    source_uri: str = "" # URI pointing to the actual content (e.g., IPFS CID)
    version: int = 1
    previous_version_id: str = None

    def update_content(self, new_content_hash: str, new_metadata: Dict = None) -> 'KnowledgeUnit':
        """
        Creates a new version of the KU with updated content.
        """
        new_ku = KnowledgeUnit(
            author_id=self.author_id,
            content_hash=new_content_hash,
            metadata=new_metadata if new_metadata else self.metadata.copy(),
            source_uri=self.source_uri, # This might change if content location changes
            version=self.version + 1,
            previous_version_id=self.id
        )
        return new_ku

    def __repr__(self):
        return f"KnowledgeUnit(id='{self.id}', author='{self.author_id}', version={self.version})"

class KnowledgeGraph:
    """
    Manages relationships between Knowledge Units.
    Placeholder for now, will be expanded with graph database interactions.
    """
    def __init__(self):
        self.relations: List[Dict[str, str]] = [] # e.g., {"from_ku": ku_id1, "to_ku": ku_id2, "type": "cites"}

    def add_relation(self, from_ku_id: str, to_ku_id: str, relation_type: str):
        self.relations.append({
            "from_ku": from_ku_id,
            "to_ku": to_ku_id,
            "type": relation_type
        })

    def get_related_kus(self, ku_id: str) -> List[Dict[str, str]]:
        related = []
        for rel in self.relations:
            if rel["from_ku"] == ku_id or rel["to_ku"] == ku_id:
                related.append(rel)
        return related

# Example usage (will be removed or moved to tests later)
if __name__ == "__main__":
    ku1 = KnowledgeUnit(author_id="user123", content_hash="abc...", metadata={"title": "Intro to SC"})
    print(ku1)
    ku2 = ku1.update_content(new_content_hash="def...", new_metadata={"title": "Intro to SC v2"})
    print(ku2)

    graph = KnowledgeGraph()
    graph.add_relation(ku1.id, ku2.id, "is_previous_version_of")
    print(graph.get_related_kus(ku1.id))
