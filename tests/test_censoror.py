import unittest
from unittest.mock import Mock
from censoror import analyze_entities

class TestAnalyzeEntities(unittest.TestCase):

    def test_analyze_entities_name(self):
        # Create a mock spaCy NLP object
        mock_nlp = Mock()

        # Create mock SpaCy entities
        mock_ent1 = Mock(text="John Doe", label_="PERSON")
        mock_ent2 = Mock(text="Jane Smith", label_="PERSON")
        mock_ents = [mock_ent1, mock_ent2]

        # Configure the mock NLP object to return the mock entities
        mock_nlp.return_value.ents = mock_ents

        # Test case for name entities
        text_content = "Hello, my name is John Doe, and this is Jane Smith."
        expected_entities = ["John Doe", "Jane Smith"]
        
        result, count = analyze_entities(text_content)

        self.assertListEqual(result, expected_entities)

    def test_empty_input(self):
        # Test when input text is empty
        result, count = analyze_entities("")
        self.assertEqual(result, [])

    def test_no_entities(self):
        # Test with input containing no relevant entities
        text_content = "The quick brown fox jumps over the lazy dog."
        result, count = analyze_entities(text_content)
        self.assertEqual(result, [])

    def test_entities(self):
        # Test with input containing a mix of relevant and irrelevant entities
        text_content = "Meeting on 2024-03-15 at 2:30 PM. Address: 4000 SW 37th BLVD. The Phone no. for the receptionist is 352-378-4990"
        result, count = analyze_entities(text_content)
        expected_entities = ["352-378-4990", "2024-03-15 at 2:30 PM.", "4000 SW 37th BLVD"]
        self.assertEqual(result, expected_entities)

if __name__ == '__main__':
    unittest.main()