import unittest
import os
import sys
import csv
import io

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import cross_reference
except ImportError:
    cross_reference = None

class TestCrossReference(unittest.TestCase):
    def test_intersection_logic(self):
        """Test that the intersection logic correctly identifies overlapping IDs."""
        if cross_reference is None:
            self.skipTest("cross_reference module not implemented")
        study_cpgs = ["cg00000001", "cg00000002"]
        ref_cpgs = ["cg00000002", "cg00000003"]
        
        overlap = cross_reference.intersect(study_cpgs, ref_cpgs)
        self.assertEqual(overlap, ["cg00000002"])

    def test_load_master_data(self):
        """Test loading master study data and parsing lists."""
        if cross_reference is None:
            self.skipTest("cross_reference module not implemented")
        csv_content = """pmid,cpgs,genes
12345,"cg1; \ncg2","G1; \nG2" """
        f = io.StringIO(csv_content.strip())
        data = cross_reference.load_master_data(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pmid'], "12345")
        self.assertIn("cg1", data[0]['cpgs'])
        self.assertIn("G1", data[0]['genes'])

if __name__ == '__main__':
    unittest.main()
