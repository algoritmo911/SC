import unittest
import uuid
from sc.models import KnowledgeUnit
from sc.services.ku_generator import generate_ku_from_prompt

class TestKUGenerator(unittest.TestCase):

    def test_generate_ku_from_prompt_basic(self):
        """
        Test basic generation of a KnowledgeUnit from a prompt.
        """
        prompt = "Create a simple test KU."
        context = {"test_type": "smoke", "complexity": "low"}

        ku = generate_ku_from_prompt(prompt, context)

        self.assertIsNotNone(ku)
        self.assertIsInstance(ku, KnowledgeUnit)

        # Check ID (should be a UUID string)
        self.assertIsInstance(ku.id, str)
        try:
            uuid.UUID(ku.id, version=4)
        except ValueError:
            self.fail("KU ID is not a valid UUID v4 string.")

        # Check quantum_fingerprint (placeholder, should be non-empty string)
        self.assertIsInstance(ku.quantum_fingerprint, str)
        self.assertTrue(ku.quantum_fingerprint.startswith("qfp_"))

        # Check entropy_signature (placeholder, should be float)
        self.assertIsInstance(ku.entropy_signature, float)
        # Based on current placeholder logic in models.py for string data
        expected_data_len = len(str({"prompt": prompt, "context": context, "generated_text": f"Generated content for prompt: '{prompt}' with context: {context}"}))
        self.assertGreaterEqual(ku.entropy_signature, 0.0) # Simplistic check for now

        # Check tags (should be a list of strings, possibly empty)
        self.assertIsInstance(ku.tags, list)
        if ku.tags: # If tags are generated
            for tag in ku.tags:
                self.assertIsInstance(tag, str)

        # Check linked_ku_ids (should be an empty list by default)
        self.assertIsInstance(ku.linked_ku_ids, list)
        self.assertEqual(len(ku.linked_ku_ids), 0)

        # Check data (should contain prompt, context, and generated_text)
        self.assertIsInstance(ku.data, dict)
        self.assertIn("prompt", ku.data)
        self.assertEqual(ku.data["prompt"], prompt)
        self.assertIn("context", ku.data)
        self.assertEqual(ku.data["context"], context)
        self.assertIn("generated_text", ku.data)
        self.assertTrue(ku.data["generated_text"].startswith("Generated content for prompt:"))

    def test_generate_ku_from_prompt_empty_context(self):
        """
        Test KU generation with an empty context.
        """
        prompt = "Another test KU with no context."
        context = {}

        ku = generate_ku_from_prompt(prompt, context)
        self.assertIsNotNone(ku)
        self.assertIsInstance(ku, KnowledgeUnit)
        self.assertEqual(ku.data["context"], context)

    def test_generate_ku_uniqueness(self):
        """
        Test that multiple calls generate KUs with unique IDs and fingerprints.
        """
        prompt1 = "First unique KU"
        ku1 = generate_ku_from_prompt(prompt1, {})

        prompt2 = "Second unique KU"
        ku2 = generate_ku_from_prompt(prompt2, {})

        self.assertNotEqual(ku1.id, ku2.id)
        self.assertNotEqual(ku1.quantum_fingerprint, ku2.quantum_fingerprint)
        # Entropy might be the same if prompts lead to similar length generated_text,
        # so not strictly checking for inequality here with current placeholder.

if __name__ == '__main__':
    unittest.main()
