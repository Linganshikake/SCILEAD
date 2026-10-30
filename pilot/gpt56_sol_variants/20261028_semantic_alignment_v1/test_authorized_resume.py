import unittest,tempfile,json
from pathlib import Path
from runtime_policy import offline_guard
offline_guard()
import httpx
import variant_runtime as runtime
import authorized_resume as a

class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=a.ROOT);self.p=Path(self.tmp.name);self.calls=[]
  runtime.save(self.p/'request.json',runtime.frozen.payload([{'role':'system','content':'synthetic'},{'role':'user','content':'synthetic'}]))
  runtime.save(self.p/'state.json',{'status':'UNKNOWN_TRANSPORT_ERROR','error_type':'RemoteProtocolError'})
  self.auth={'authorized':True,'max_additional_attempts':1,'request_sha256':runtime.sha(self.p/'request.json'),'original_state_sha256':runtime.sha(self.p/'state.json')}
 def tearDown(self):self.tmp.cleanup()
 def client(self,status=200,finish='stop'):
  def handle(request):
   self.calls.append(json.loads(request.content))
   return httpx.Response(status,json={'model':runtime.MODEL,'choices':[{'finish_reason':finish,'message':{'content':'synthetic-answer'}}]})
  return httpx.Client(transport=httpx.MockTransport(handle))
 def authorize(self):runtime.save(self.p/'manual_recovery_authorization.json',self.auth)
 def test_missing_approval_no_call(self):
  with self.assertRaises(FileNotFoundError):a.recover(self.p,self.client(),'synthetic-key',runtime)
  self.assertEqual(self.calls,[])
 def test_exact_resend_original_retained_second_call_blocked(self):
  self.authorize();old=runtime.sha(self.p/'state.json');a.recover(self.p,self.client(),'synthetic-key',runtime)
  self.assertEqual(self.calls,[runtime.read(self.p/'request.json')]);self.assertEqual(runtime.sha(self.p/'state.json'),old)
  self.assertEqual(runtime.read(self.p/'accepted.json')['response_relative_path'],'retry_1/response.json')
  with self.assertRaises(AssertionError):a.recover(self.p,self.client(),'synthetic-key',runtime)
  self.assertEqual(len(self.calls),1)
 def test_failed_retry_never_repeated(self):
  self.authorize()
  for _ in range(2):
   with self.assertRaises((RuntimeError,AssertionError)):a.recover(self.p,self.client(500),'synthetic-key',runtime)
  self.assertEqual(len(self.calls),1);self.assertFalse((self.p/'accepted.json').exists())
 def test_changed_request_blocks(self):
  self.authorize();runtime.save(self.p/'request.json',runtime.frozen.payload([]))
  with self.assertRaises(AssertionError):a.recover(self.p,self.client(),'synthetic-key',runtime)
  self.assertEqual(self.calls,[])
 def test_changed_original_state_blocks(self):
  self.authorize();runtime.save(self.p/'state.json',{'status':'HTTP_ERROR','http_status':403})
  with self.assertRaises(AssertionError):a.recover(self.p,self.client(),'synthetic-key',runtime)
  self.assertEqual(self.calls,[])
 def test_nonstop_not_accepted(self):
  self.authorize()
  with self.assertRaises(ValueError):a.recover(self.p,self.client(finish='length'),'synthetic-key',runtime)
  self.assertFalse((self.p/'accepted.json').exists())

if __name__=='__main__':unittest.main()
