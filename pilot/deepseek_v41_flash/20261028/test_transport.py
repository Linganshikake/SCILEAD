import unittest,tempfile,json
from pathlib import Path
import httpx
import transport as t
from result_compat import convert

class Audit(unittest.TestCase):
 def body(self,content='[]',model=t.MODEL,reason='stop'):
  return {'model':model,'choices':[{'finish_reason':reason,'message':{'content':content}}]}
 def test_parameters(self):
  p=t.payload([]);self.assertEqual(set(p),{'model','messages','thinking','reasoning_effort','stream'});self.assertEqual(p['model'],'deepseek-flash')
 def test_result_compatible(self):
  for result in ('1','1.25','"3.40"','0','-0.5'):
   text='[{"Task":"t","Dataset":"d","Metric":"m","Result":'+result+'}]'
   r,a=convert(text);self.assertIsInstance(r[0]['Result'],str);self.assertEqual(r[0]['Task'],'t')
 def test_invalid_result_rejected(self):
  for v in ('null','true','[]','{}','NaN','Infinity','1.234567890123456789'):
   with self.assertRaises(ValueError):convert('[{"Task":"t","Dataset":"d","Metric":"m","Result":'+v+'}]')
 def test_non_result_and_duplicates(self):
  for text in ('[{"Task":null,"Dataset":"d","Metric":"m","Result":"1"}]','[{"Task":"t","Task":"x","Dataset":"d","Metric":"m","Result":"1"}]','[{"Task":"t"}]','```json\n[]\n```','[','{}'):
   with self.assertRaises(ValueError):t.validate(self.body(text),True)
 def test_no_semantic_repair(self):
  text='[{"Task":"WRONG","Dataset":"BASELINE","Metric":"F1","Result":4696},{"Task":"WRONG","Dataset":"BASELINE","Metric":"F1","Result":4696}]'
  r=t.validate(self.body(text),True);self.assertEqual(len(r),2);self.assertEqual(r[0],r[1]);self.assertEqual(r[0]['Result'],'4696')
 def test_protocol(self):
  for b in (self.body(reason='length'),self.body(model='other'),self.body(content='')):
   with self.assertRaises(ValueError):t.validate(b,True)
 def test_normalization_exact_raw(self):self.assertEqual(t.validate(self.body(content=' None\n'),False),' None\n')
 def test_no_retry(self):
  for code in (200,403,500):
   calls=[]
   def handler(req):calls.append(req);return httpx.Response(code,json=self.body())
   with tempfile.TemporaryDirectory(dir=t.ROOT) as d,httpx.Client(transport=httpx.MockTransport(handler)) as c:
    p=Path(d)/'request'
    if code==200:t.one_request(c,p,t.payload([]),'synthetic-key',t.BASE+'/chat/completions')
    else:
     with self.assertRaises(RuntimeError):t.one_request(c,p,t.payload([]),'synthetic-key',t.BASE+'/chat/completions')
    with self.assertRaises(FileExistsError):t.one_request(c,p,t.payload([]),'synthetic-key',t.BASE+'/chat/completions')
    self.assertEqual(len(calls),1);self.assertNotIn('synthetic-key',(p/'request.json').read_text())
 def test_timeout_no_retry(self):
  calls=[]
  def handler(req):calls.append(req);raise httpx.ReadTimeout('test')
  with tempfile.TemporaryDirectory(dir=t.ROOT) as d,httpx.Client(transport=httpx.MockTransport(handler)) as c:
   p=Path(d)/'request'
   with self.assertRaises(RuntimeError):t.one_request(c,p,t.payload([]),'synthetic-key',t.BASE+'/chat/completions')
   self.assertEqual(t.load(p/'state.json')['status'],'UNKNOWN_TRANSPORT_ERROR')
   with self.assertRaises(FileExistsError):t.one_request(c,p,t.payload([]),'synthetic-key',t.BASE+'/chat/completions')
   self.assertEqual(len(calls),1)
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Audit);r=unittest.TextTestRunner(verbosity=2).run(suite)
 t.save(t.ROOT/'offline_test_results.json',{'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'passed':r.wasSuccessful(),'model_calls':0})
 raise SystemExit(not r.wasSuccessful())
