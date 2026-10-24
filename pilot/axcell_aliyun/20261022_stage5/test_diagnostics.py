import unittest
from diagnostics import strict_number,equal_number,maximum_matching
class DiagnosticTests(unittest.TestCase):
    def test_no_substring_or_unit_repair(self):
        self.assertFalse(equal_number('91','91.85'));self.assertTrue(equal_number('4696.0',4696))
        self.assertFalse(equal_number('0.9185','91.85'));self.assertIsNone(strict_number('91.85%'));self.assertIsNone(strict_number('NaN'))
    def test_duplicate_cannot_reuse_gold(self):
        self.assertEqual(len(maximum_matching([1,1],[1],lambda a,b:a==b)),1)
    def test_augmenting_path_not_greedy(self):
        pairs=maximum_matching(['broad','narrow'],[1,2],lambda a,b:a=='broad' or b==1)
        self.assertEqual(set(pairs),{(0,1),(1,0)})
    def test_empty(self):self.assertEqual(maximum_matching([],[],lambda a,b:True),[])
if __name__=='__main__':unittest.main()
