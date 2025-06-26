import unittest
from fastapi.testclient import TestClient

# Assuming the FastAPI app for graph is in sc.api.graph and named 'app'
# If it's a router, we might need to mount it on a dummy app for testing.
# For now, let's assume sc.api.graph.app is the FastAPI instance.
# We need to ensure that the in-memory data stores are clean for each test or test class.

from sc.api.graph import app as graph_app # Direct import of the app
from sc.services import ku_graph # To directly manipulate or check graph state

# We also need a way to manage the KUs if the graph API checks for KU existence.
# The current graph API has KU existence checks commented out. If they were active,
# we'd need to interact with sc.api.knowledge.knowledge_units_db as well.
# from sc.api.knowledge import knowledge_units_db


class TestGraphAPI(unittest.TestCase):

    def setUp(self):
        """
        Set up a TestClient for each test.
        Clear any existing graph data before each test.
        """
        self.client = TestClient(graph_app)
        ku_graph.ku_links.clear() # Clear graph links
        # If KU existence checks were active in graph API, also clear knowledge_units_db
        # knowledge_units_db.clear()
        # And potentially pre-populate with some KUs for testing link creation.
        # For example:
        # knowledge_units_db["ku_A"] = KnowledgeUnit(id="ku_A", quantum_fingerprint="qfpA", entropy_signature=1.0)
        # knowledge_units_db["ku_B"] = KnowledgeUnit(id="ku_B", quantum_fingerprint="qfpB", entropy_signature=1.0)
        # knowledge_units_db["ku_C"] = KnowledgeUnit(id="ku_C", quantum_fingerprint="qfpC", entropy_signature=1.0)


    def tearDown(self):
        """
        Clean up after tests if necessary.
        """
        ku_graph.ku_links.clear()
        # knowledge_units_db.clear()

    def test_link_knowledge_units_success(self):
        """
        Test successful creation of a link between two KUs.
        """
        response = self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_test_1", "to_ku_id": "ku_test_2", "weight": 0.75}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["message"], "Link created successfully")
        self.assertEqual(data["from_ku_id"], "ku_test_1")
        self.assertEqual(data["to_ku_id"], "ku_test_2")
        self.assertEqual(data["weight"], 0.75)

        # Verify in the service layer
        links_from_ku1 = ku_graph.get_links_from("ku_test_1")
        self.assertIsNotNone(links_from_ku1)
        self.assertEqual(len(links_from_ku1), 1)
        self.assertEqual(links_from_ku1[0], ("ku_test_2", 0.75))

    def test_link_knowledge_units_update_weight(self):
        """
        Test updating the weight of an existing link.
        """
        self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_test_A", "to_ku_id": "ku_test_B", "weight": 0.5}
        ) # Initial link
        response = self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_test_A", "to_ku_id": "ku_test_B", "weight": 0.9}
        ) # Update
        self.assertEqual(response.status_code, 201) # add_link in service layer updates, API returns 201
        data = response.json()
        self.assertEqual(data["weight"], 0.9)

        links_from_kuA = ku_graph.get_links_from("ku_test_A")
        self.assertIsNotNone(links_from_kuA)
        self.assertEqual(len(links_from_kuA), 1)
        self.assertEqual(links_from_kuA[0], ("ku_test_B", 0.9))

    def test_link_knowledge_units_invalid_weight_too_high(self):
        """
        Test link creation with weight > 1.0 (should be caught by Pydantic).
        """
        response = self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_fail_1", "to_ku_id": "ku_fail_2", "weight": 1.1}
        )
        self.assertEqual(response.status_code, 422) # Unprocessable Entity for Pydantic validation error

    def test_link_knowledge_units_invalid_weight_too_low(self):
        """
        Test link creation with weight < 0.0 (should be caught by Pydantic).
        """
        response = self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_fail_3", "to_ku_id": "ku_fail_4", "weight": -0.1}
        )
        self.assertEqual(response.status_code, 422) # Unprocessable Entity

    def test_link_knowledge_unit_to_itself(self):
        """
        Test trying to link a KU to itself.
        """
        response = self.client.post(
            "/api/graph/link",
            json={"from_ku_id": "ku_self", "to_ku_id": "ku_self", "weight": 0.5}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot link a Knowledge Unit to itself", response.json()["detail"])

    def test_get_outgoing_links_success(self):
        """
        Test retrieving outgoing links for a KU.
        """
        self.client.post("/api/graph/link", json={"from_ku_id": "ku_source", "to_ku_id": "ku_target1", "weight": 0.8})
        self.client.post("/api/graph/link", json={"from_ku_id": "ku_source", "to_ku_id": "ku_target2", "weight": 0.6})

        response = self.client.get("/api/graph/links/ku_source")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ku_id"], "ku_source")
        self.assertIsInstance(data["links"], list)
        self.assertEqual(len(data["links"]), 2)
        # Order might not be guaranteed, so check for presence
        expected_links = [
            {"to_ku_id": "ku_target1", "weight": 0.8},
            {"to_ku_id": "ku_target2", "weight": 0.6}
        ]
        self.assertCountEqual(data["links"], expected_links) # Checks elements regardless of order

    def test_get_outgoing_links_no_links(self):
        """
        Test retrieving links for a KU that exists (implicitly, by querying) but has no outgoing links.
        """
        # ku_graph.add_link("ku_no_outgoing_links", "some_other_ku", 0.1) # This would be an incoming link
        # To ensure "ku_no_outgoing_links" is known, we don't need to do anything if not checking KU existence.
        # If KU existence was checked, we'd add it to knowledge_units_db.
        response = self.client.get("/api/graph/links/ku_no_outgoing_links")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["ku_id"], "ku_no_outgoing_links")
        self.assertEqual(data["links"], [])

    def test_get_outgoing_links_ku_not_found(self):
        """
        Test retrieving links for a KU that has no record in the graph data.
        This is similar to "no links" with current implementation as get_links_from returns None.
        If KU existence was checked and it wasn't in knowledge_units_db, API would 404.
        """
        response = self.client.get("/api/graph/links/ku_does_not_exist_in_graph")
        self.assertEqual(response.status_code, 200) # Current API returns 200 with empty list
        data = response.json()
        self.assertEqual(data["ku_id"], "ku_does_not_exist_in_graph")
        self.assertEqual(data["links"], [])

    def test_get_all_graph_links_empty(self):
        """
        Test retrieving all links when the graph is empty.
        """
        response = self.client.get("/api/graph/all_links")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})

    def test_get_all_graph_links_with_data(self):
        """
        Test retrieving all links when there's data in the graph.
        """
        self.client.post("/api/graph/link", json={"from_ku_id": "k1", "to_ku_id": "k2", "weight": 0.1})
        self.client.post("/api/graph/link", json={"from_ku_id": "k1", "to_ku_id": "k3", "weight": 0.2})
        self.client.post("/api/graph/link", json={"from_ku_id": "k2", "to_ku_id": "k3", "weight": 0.3})

        response = self.client.get("/api/graph/all_links")
        self.assertEqual(response.status_code, 200)
        expected_graph = {
            "k1": [["k2", 0.1], ["k3", 0.2]], # JSON conversion of tuples results in lists
            "k2": [["k3", 0.3]]
        }
        # The service returns list of tuples, API returns this dict directly.
        # FastAPI/TestClient will deserialize JSON arrays as lists.
        self.assertEqual(response.json(), expected_graph)

if __name__ == '__main__':
    unittest.main()
