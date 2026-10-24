import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_batch as b
import msvcrt

class ResumeTests(unittest.TestCase):
 def test_windows_locked_control_file_scan(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);lock=p/'batch_process.lock';lock.write_bytes(b'0')
   with lock.open('r+b') as f:
    msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
    with self.assertRaises(PermissionError):lock.read_bytes()
    self.assertTrue(b.secret_scan(p,'dummy-secret'))
    (p/'response.txt').write_text('dummy-secret')
    self.assertFalse(b.secret_scan(p,'dummy-secret'))
 def test_success_is_reused_without_network(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);req=b.payload([{'role':'user','content':'x'}])
   b.save(p/'request.json',req);b.save(p/'state.json',{'status':'RECEIVED','http_status':200})
   res={'model':b.MODEL,'choices':[{'finish_reason':'stop','message':{'content':'[]'}}]}
   b.save(p/'response.json',res);(p/'attempt.lock').write_text('sent')
   with patch.object(b,'one_request',side_effect=AssertionError('Must not send')):
    self.assertEqual(b.request(None,p,req,'key','url',True)[1],[])
 def test_unknown_is_not_retried(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'attempt.lock').write_text('sent');b.save(p/'state.json',{'status':'SENDING'})
   with patch.object(b,'one_request',side_effect=AssertionError('Must not send')):
    with self.assertRaises(b.ServiceStop):b.request(None,p,b.payload([]),'key','url',True)
 def test_changed_payload_cannot_reuse_response(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'attempt.lock').write_text('sent');b.save(p/'state.json',{'status':'RECEIVED','http_status':200});b.save(p/'request.json',{'old':True})
   with self.assertRaises(b.ServiceStop):b.request(None,p,b.payload([]),'key','url',True)

if __name__=='__main__':unittest.main()
