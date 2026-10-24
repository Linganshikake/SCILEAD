import unittest,json
from parser import parse
A='{"Task":"T","Dataset":"D","Metric":"M","Result":26.60}'
B='{"Task":"U","Dataset":"E","Metric":"N","Result":"1e-3"}'
class ParserTests(unittest.TestCase):
    def ok(self,text,n):
        v=parse(text);self.assertTrue(v['ok'],v);self.assertEqual(len(json.loads(v['text'])),n);return v
    def bad(self,text):self.assertFalse(parse(text)['ok'])
    def test_valid_single_verbatim(self):self.assertEqual(self.ok('['+A+']',1)['text'],'['+A+']')
    def test_valid_single_outer_whitespace_verbatim(self):self.assertEqual(self.ok('\n\n['+A+']\n',1)['text'],'\n\n['+A+']\n')
    def test_three_complete_arrays(self):
        v=self.ok('['+A+']\n['+B+']\n['+A+']',3);self.assertEqual(v['text'],'['+A+','+B+','+A+']')
    def test_neutral_headings(self):self.ok('Here are the extracted tuples in JSON format:\n**T**\n['+A+']\n**U**\n['+B+']',2)
    def test_brackets_escaped_string(self):
        row=json.dumps({'Task':'T','Dataset':'D [x] \\" ]','Metric':'M','Result':'1'});self.ok('['+row+']\n['+row+']',2)
    def test_duplicates_preserved(self):self.assertEqual(self.ok('['+A+'] ['+A+']',2)['text'],'['+A+','+A+']')
    def test_alternative_rejected(self):self.bad('['+A+']\nCorrected answer:\n['+B+']')
    def test_unknown_prose_rejected(self):self.bad('These results may be wrong:\n['+A+']')
    def test_incomplete_key(self):self.bad('['+A+', {"Task":"U","Metri')
    def test_only_missing_outer_close(self):self.assertEqual(self.ok('['+A,1)['text'],'['+A+']')
    def test_trailing_comma_rejected(self):self.bad('['+A+',')
    def test_partial_number_rejected(self):self.bad('[{"Task":"T","Dataset":"D","Metric":"M","Result":1e')
    def test_duplicate_key(self):self.bad('['+A.replace('"Task":"T"','"Task":"T","Task":"U"')+']')
    def test_nested_arrays_rejected(self):self.bad('[['+A+']]')
    def test_missing_field_not_filled_from_heading(self):self.bad('**T**\n[{"Dataset":"D","Metric":"M","Result":1}]')
    def test_fences(self):self.ok('Here are the extracted tuples in JSON format:\n```json\n['+A+']\n```',1)
    def test_multiple_incomplete_groups_rejected(self):self.bad('['+A+']\n['+B)
    def test_nonfinite_bool_rejected(self):
        for x in ['NaN','1e999','true']:self.bad('['+A.replace('26.60',x)+']')
    def test_heading_must_be_group_label(self):self.bad('**Better answer**\n['+A+']')
if __name__=='__main__':unittest.main(verbosity=2)
