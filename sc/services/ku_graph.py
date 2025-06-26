from typing import Dict, List, Tuple, Optional

# In-memory storage for the Knowledge Unit graph.
# Structure:
# {
# "ku_id_1": [("ku_id_2", 0.8), ("ku_id_3", 0.5)], # from_ku_id_1 links to ku_id_2 with weight 0.8
# "ku_id_2": [("ku_id_4", 0.9)]
# }
# This represents a directed graph where edges have weights.
# We could also store reverse links if needed for quick lookups,
# or use a more sophisticated graph library for larger datasets.

ku_links: Dict[str, List[Tuple[str, float]]] = {}

# Optional: To ensure KUs exist before linking, we might need a reference
# to the main KU database or a function to check existence.
# For now, we'll assume KU IDs are valid if provided.
# from sc.api.knowledge import knowledge_units_db # Avoid circular dependency if possible, pass as arg or use callback

def add_link(from_ku_id: str, to_ku_id: str, weight: float) -> bool:
    """
    Adds a directed link with a weight between two Knowledge Units.

    Args:
        from_ku_id (str): The ID of the source Knowledge Unit.
        to_ku_id (str): The ID of the target Knowledge Unit.
        weight (float): The weight of the link (e.g., semantic similarity, relevance).

    Returns:
        bool: True if the link was added or updated, False otherwise (e.g., invalid weight).
    """
    if not (0.0 <= weight <= 1.0): # Assuming weight is normalized between 0 and 1
        print(f"Error: Link weight must be between 0.0 and 1.0. Received: {weight}")
        return False

    # Optional: Check if KUs exist
    # if from_ku_id not in knowledge_units_db or to_ku_id not in knowledge_units_db:
    #     print(f"Error: One or both KU IDs do not exist: {from_ku_id}, {to_ku_id}")
    #     return False

    if from_ku_id not in ku_links:
        ku_links[from_ku_id] = []

    # Check if the link already exists to update weight, or add new
    existing_link_index = -1
    for i, (target_id, _) in enumerate(ku_links[from_ku_id]):
        if target_id == to_ku_id:
            existing_link_index = i
            break

    if existing_link_index != -1:
        ku_links[from_ku_id][existing_link_index] = (to_ku_id, weight)
        print(f"Updated link from {from_ku_id} to {to_ku_id} with new weight {weight}")
    else:
        ku_links[from_ku_id].append((to_ku_id, weight))
        print(f"Added link from {from_ku_id} to {to_ku_id} with weight {weight}")

    return True

def get_links_from(ku_id: str) -> Optional[List[Tuple[str, float]]]:
    """
    Retrieves all outgoing links (and their weights) for a given Knowledge Unit.

    Args:
        ku_id (str): The ID of the source Knowledge Unit.

    Returns:
        Optional[List[Tuple[str, float]]]: A list of (target_ku_id, weight) tuples,
                                           or None if the KU has no outgoing links or doesn't exist.
    """
    return ku_links.get(ku_id)

def get_all_links() -> Dict[str, List[Tuple[str, float]]]:
    """
    Returns the entire graph.
    """
    return ku_links

if __name__ == '__main__':
    # Example Usage
    print("Initial graph:", get_all_links())

    add_link("ku1", "ku2", 0.75)
    add_link("ku1", "ku3", 0.5)
    add_link("ku2", "ku3", 0.9)

    print("\nGraph after adding links:", get_all_links())

    print("\nLinks from ku1:", get_links_from("ku1"))
    print("Links from ku2:", get_links_from("ku2"))
    print("Links from ku3 (should be None or empty):", get_links_from("ku3"))

    # Update a link
    add_link("ku1", "ku2", 0.85)
    print("\nGraph after updating ku1->ku2 link:", get_all_links())

    # Invalid weight
    add_link("ku1", "ku4", 1.5) # Should fail

    # For testing existence checks (if implemented with a KU DB)
    # Assuming ku_db exists and is populated
    # class MockKUDB:
    #     def __init__(self):
    #         self.db = {"ku1": {}, "ku2": {}, "ku3": {}}
    #     def __contains__(self, key):
    #         return key in self.db
    # knowledge_units_db = MockKUDB() # Replace the import at the top for testing
    # add_link("ku1", "non_existent_ku", 0.5) # Should fail if existence check is active
    # add_link("non_existent_ku", "ku1", 0.5) # Should fail
    print("\nFinal graph state:", get_all_links())
