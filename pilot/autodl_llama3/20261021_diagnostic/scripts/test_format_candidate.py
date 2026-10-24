import unittest,json
from format_candidate import audit
ROW='{"Task":"T","Dataset":"D","Metric":"M","Result":90.32}'
class Tests(unittest.TestCase):
    def test_exact_list_and_numeric_preserved(self):
        raw='['+ROW+']';r=audit(raw);self.assertTrue(r['raw_json_valid']);self.assertEqual(r['candidate_text'],raw);self.assertEqual(r['result_types'],['float']);self.assertTrue(r['official_schema_acceptable'])
    def test_single_prefix_candidate(self):
        raw='\n\nHere are the extracted tuples in JSON format:\n\n['+ROW+']';r=audit(raw);self.assertFalse(r['raw_json_valid']);self.assertTrue(r['candidate_eligible']);self.assertEqual(r['candidate_text'],'['+ROW+']');self.assertTrue(r['record_values_unchanged'])
    def test_multiple_arrays_reject(self):self.assertFalse(audit('['+ROW+']\n['+ROW+']')['candidate_eligible'])
    def test_truncated_reject(self):self.assertFalse(audit('Here are the extracted tuples in JSON format:\n['+ROW)['candidate_eligible'])
    def test_duplicate_key_reject(self):self.assertFalse(audit('[{"Task":"T","Task":"Other","Dataset":"D","Metric":"M","Result":"1"}]')['candidate_eligible'])
    def test_nonfinite_reject(self):self.assertFalse(audit('['+ROW.replace('90.32','NaN')+']')['candidate_eligible'])
    def test_missing_field_reject(self):self.assertFalse(audit('[{"Task":"T"}]')['candidate_eligible'])
    def test_single_object_not_wrapped(self):self.assertFalse(audit(ROW)['candidate_eligible'])
    def test_suffix_qualification_reject(self):self.assertFalse(audit('['+ROW+']\nThese results are baselines.')['candidate_eligible'])
    def test_fence_whole_array_allowed_candidate(self):self.assertTrue(audit('```json\n['+ROW+']\n```')['candidate_eligible'])
    def test_nested_values_reject(self):self.assertFalse(audit('['+ROW.replace('90.32','[1,2]')+']')['candidate_eligible'])
    def test_bad_prefix_reject(self):self.assertFalse(audit('Warning: invented examples\n['+ROW+']')['candidate_eligible'])
    def test_empty_list_is_preserved(self):self.assertTrue(audit('[]')['candidate_eligible'])
if __name__=='__main__':unittest.main()
