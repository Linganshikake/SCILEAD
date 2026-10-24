import json,unittest
from recovery_adapter import convert

class RecoveryTests(unittest.TestCase):
 def row(self,result):return '[{"Task":"T","Dataset":"D","Metric":"M","Result":'+result+'}]'
 def test_official_str_float(self):
  rows,audit=convert(self.row('0.950'))
  self.assertEqual(rows[0]['Result'],'0.95')
  self.assertEqual(audit[0]['original_numeric_literal'],'0.950')
  self.assertTrue(audit[0]['numeric_semantics_equal'])
 def test_integer_and_string_preserved(self):
  self.assertEqual(convert(self.row('123'))[0][0]['Result'],'123')
  self.assertEqual(convert(self.row('"91.80%"'))[0][0]['Result'],'91.80%')
 def test_no_rescaling_or_dedup(self):
  row=json.loads(self.row('0.918'))[0]
  output,_=convert(json.dumps([row,row]));self.assertEqual(len(output),2)
  self.assertEqual(output[0]['Result'],'0.918');self.assertEqual(output[0],output[1])
 def test_reject_null_bool_nonfinite(self):
  for value in ['null','true','false','NaN','Infinity','-Infinity']:
   with self.subTest(value=value),self.assertRaises(ValueError):convert(self.row(value))
 def test_reject_other_field_and_structure_errors(self):
  for text in ['[] garbage','{}','[{"Result":1}]',self.row('1').replace('"Task":"T"','"Task":null'),self.row('1').replace('"Result":1','"Result":1,"Result":2')]:
   with self.subTest(text=text),self.assertRaises(ValueError):convert(text)
 def test_reject_numeric_precision_loss(self):
  with self.assertRaises(ValueError):convert(self.row('0.12345678901234567890123456789'))

if __name__=='__main__':unittest.main()
