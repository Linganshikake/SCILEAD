"""No network: exercise durable single-position requests and DeepSeek wire contract."""
import importlib.util,json,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent

class Tests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE/'variant_runtime.py').exists(),'Independent DeepSeek transport not implemented')
        import variant_runtime as v
        self.v=v
        self.temp=tempfile.TemporaryDirectory(dir=HERE)
        self.root=Path(self.temp.name)
    def tearDown(self):
        if hasattr(self,'temp'):self.temp.cleanup()
    def body(self,finish='stop',model='deepseek-flash'):
        return {'model':model,'choices':[{'finish_reason':finish,'message':{'role':'assistant','content':'X'}}],'usage':{'prompt_tokens':7,'completion_tokens':1,'total_tokens':8}}
    def client(self,body=None,error=False,status=200):
        import httpx
        calls=[]
        def handler(request):
            calls.append(json.loads(request.content))
            if error:raise httpx.ReadTimeout('synthetic',request=request)
            return httpx.Response(status,json=body or self.body())
        return httpx.Client(transport=httpx.MockTransport(handler)),calls
    def test_exact_wire_and_resume_no_new_request(self):
        client,calls=self.client();messages=[{'role':'system','content':'S'},{'role':'user','content':'U'}]
        answer=self.v.durable_request(client,self.root/'call',messages,'synthetic-test-key')
        self.assertEqual(answer,'X');self.assertEqual(len(calls),1)
        self.assertEqual(calls[0],{'model':'deepseek-flash','messages':messages,'thinking':{'type':'enabled'},'reasoning_effort':'high','stream':False})
        self.assertEqual(self.v.durable_request(client,self.root/'call',messages,'synthetic-test-key'),'X')
        self.assertEqual(len(calls),1)
    def test_unknown_attempt_never_resends(self):
        client,calls=self.client(error=True)
        for _ in range(2):
            with self.assertRaises(Exception):self.v.durable_request(client,self.root/'call',[],'synthetic-test-key')
        self.assertEqual(len(calls),1)
    def test_http_failure_never_resends(self):
        client,calls=self.client(body={'error':{'code':'get_channel_failed'}},status=500)
        for _ in range(2):
            with self.assertRaises(Exception):self.v.durable_request(client,self.root/'call',[],'synthetic-test-key')
        self.assertEqual(len(calls),1)
    def test_nonstop_and_wrong_model_rejected(self):
        for i,body in enumerate([self.body('length'),self.body(model='different')]):
            client,calls=self.client(body)
            with self.assertRaises(Exception):self.v.durable_request(client,self.root/str(i),[],'synthetic-test-key')
            self.assertEqual(len(calls),1)
    def test_changed_prompt_cannot_reuse_response(self):
        client,calls=self.client()
        self.v.durable_request(client,self.root/'call',[],'synthetic-test-key')
        with self.assertRaises(Exception):self.v.durable_request(client,self.root/'call',[{'role':'user','content':'changed'}],'synthetic-test-key')
        self.assertEqual(len(calls),1)
    def test_repeated_field_different_positions_are_independent(self):
        client,calls=self.client()
        for name in ('1','2'):self.v.durable_request(client,self.root/name,[],'synthetic-test-key')
        self.assertEqual(len(calls),2)
    def test_response_without_acceptance_marker_stays_blocked_without_resend(self):
        client,calls=self.client();folder=self.root/'call'
        self.v.frozen.one_request(client,folder,self.v.frozen.payload([]),'synthetic-test-key',self.v.URL+'/chat/completions')
        for _ in range(2):
            with self.assertRaisesRegex(AssertionError,'FAILED_OR_UNKNOWN_NO_AUTOMATIC_RESEND'):
                self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.assertEqual(len(calls),1)
        self.assertFalse((folder/'accepted.json').exists())
    def test_transient_filesystem_lock_retries_only_write(self):
        from unittest.mock import patch
        actual=self.v.os.replace;seen=[]
        def replace(a,b):
            seen.append((a,b))
            if len(seen)<3:raise PermissionError('synthetic sharing conflict')
            return actual(a,b)
        with patch.object(self.v.os,'replace',side_effect=replace):
            self.v.save(self.root/'checkpoint.json',{'received':179})
        self.assertEqual(self.v.read(self.root/'checkpoint.json'),{'received':179})
        self.assertEqual(len(seen),3)
    def test_explicit_one_retry_preserves_failure_and_replays_success(self):
        folder=self.root/'call';client,calls=self.client(status=524,body={'error':'timeout'})
        with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.v.save(folder/'retry_authorization.json',{'max_additional_attempts':1,'original_request_sha256':self.v.sha(folder/'request.json'),'original_http_status':524,'authorization':'explicit test approval'})
        good,gcalls=self.client()
        try:answer=self.v.durable_request(good,folder,[],'synthetic-test-key')
        except Exception as e:self.fail('Explicit single retry not supported: '+str(e))
        self.assertEqual(answer,'X');self.assertEqual(len(gcalls),1)
        self.assertEqual(self.v.read(folder/'state.json')['http_status'],524)
        self.assertEqual(self.v.read(folder/'response.json'),{'error':'timeout'})
        self.assertEqual(self.v.durable_request(good,folder,[],'synthetic-test-key'),'X')
        self.assertEqual(len(gcalls),1)
    def test_explicit_retry_does_not_allow_third_attempt(self):
        folder=self.root/'call';client,calls=self.client(status=524,body={'error':'timeout'})
        with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.v.save(folder/'retry_authorization.json',{'max_additional_attempts':1,'original_request_sha256':self.v.sha(folder/'request.json'),'original_http_status':524,'authorization':'explicit test approval'})
        for _ in range(2):
            with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.assertEqual(len(calls),2)
    def test_explicit_quota_recovery_requires_exact_code_and_one_attempt(self):
        folder=self.root/'call';client,calls=self.client(status=403,body={'error':{'code':'insufficient_user_quota'}})
        with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.v.save(folder/'retry_authorization.json',{'max_additional_attempts':1,'original_request_sha256':self.v.sha(folder/'request.json'),'original_http_status':403,'original_error_code':'insufficient_user_quota','balance_replenished_confirmed':True,'authorization':'explicit test approval'})
        good,gcalls=self.client()
        self.assertEqual(self.v.durable_request(good,folder,[],'synthetic-test-key'),'X')
        self.assertEqual(self.v.durable_request(good,folder,[],'synthetic-test-key'),'X')
        self.assertEqual(len(gcalls),1);self.assertEqual(self.v.read(folder/'state.json')['http_status'],403)
    def test_quota_authorization_cannot_retry_other_forbidden_error(self):
        folder=self.root/'call';client,calls=self.client(status=403,body={'error':{'code':'different_forbidden_error'}})
        with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.v.save(folder/'retry_authorization.json',{'max_additional_attempts':1,'original_request_sha256':self.v.sha(folder/'request.json'),'original_http_status':403,'original_error_code':'insufficient_user_quota','balance_replenished_confirmed':True,'authorization':'explicit test approval'})
        with self.assertRaises(Exception):self.v.durable_request(client,folder,[],'synthetic-test-key')
        self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main(verbosity=2)
