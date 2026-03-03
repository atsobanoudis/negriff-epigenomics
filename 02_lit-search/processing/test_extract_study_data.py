import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys

# Add the current directory to sys.path to import the script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import extract_study_data

class TestExtractStudyData(unittest.TestCase):

    def test_prompt_generation(self):
        """Test that the prompt includes necessary standardization rules and placeholders."""
        content = "Sample study content"
        filename = "12345.md"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout='{"pmid": "12345", "title": "Test Title", "sample": "Blood", "ewas_platform": "EPIC", "exposure": "Maltreatment", "cpgs": "cg123; \\n", "genes": "GENE1; \\n"}', stderr='')
            extract_study_data.run_gemini(content, filename)
            
            args, kwargs = mock_run.call_args
            prompt = args[0][1] 
            
            self.assertIn("cg00000000", prompt)
            self.assertIn("NR3C1", prompt)
            self.assertIn("SLC6A4", prompt)
            self.assertIn("'; \\n'", prompt) 
            self.assertIn("HGNC", prompt)
            self.assertIn("Sample study content", prompt)

    def test_parsing_json_with_markdown_blocks(self):
        """Test that the script correctly extracts JSON even if Gemini wraps it in markdown code blocks."""
        raw_output = "Here is the result:\n```json\n{\"pmid\": \"12345\", \"title\": \"T\", \"sample\": \"Blood\", \"ewas_platform\": \"EPIC\", \"exposure\": \"E\", \"cpgs\": \"c; \\n\", \"genes\": \"g; \\n\"}\n```\nHope this helps."
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=raw_output, stderr='')
            result = extract_study_data.run_gemini("content", "file.md")
            
            self.assertIsNotNone(result)
            self.assertEqual(result['pmid'], "12345")
            self.assertEqual(result['title'], "T")

    def test_failed_json_extraction(self):
        """Test handling of output that contains no JSON."""
        raw_output = "I am sorry, I couldn't find any data."
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout=raw_output, stderr='')
            result = extract_study_data.run_gemini("content", "file.md")
            
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
