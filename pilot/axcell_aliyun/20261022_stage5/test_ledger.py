import unittest, tempfile,json
from pathlib import Path
import httpx
from ledger import FrozenLedger

MODEL='gpt-4.1-2025-04-14'
def entry():return {'request_id':'norm-0001','checkpoint_cache_key':'unique-original-position','payload':{'model':MODEL,'temperature':0,'seed':0,'n':1,'stream':False,'messages':[{'role':'system','content':'Match the exact item.'},{'role':'user','content':'Input: value'}]}}
def response(finish='stop',model=MODEL,answer='None'):
    return {'id':'mock-only','object':'chat.completion','created':0,'model':model,'choices':[{'index':0,'message':{'role':'assistant','content':answer},'finish_reason':finish}],'usage':{'prompt_tokens':12,'completion_tokens':1,'total_tokens':13}}
class LedgerTests(unittest.TestCase):
    def test_success_and_resume_do_not_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[]
            def handler(req):calls.append(json.loads(req.content));return httpx.Response(200,json=response())
            ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(handler))
            self.assertEqual(ledger.invoke(entry()['payload']['messages']).content,'None');ledger.close()
            self.assertEqual(calls,[entry()['payload']])
            ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(handler))
            self.assertEqual(ledger.invoke(entry()['payload']['messages']).content,'None');ledger.close();self.assertEqual(len(calls),1)
    def test_failed_attempt_never_retried(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[]
            def handler(req):calls.append(1);return httpx.Response(502,json={'error':{'message':'gateway failure','type':'server_error'}})
            for _ in range(2):
                ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(handler))
                with self.assertRaises(Exception):ledger.invoke(entry()['payload']['messages'])
                ledger.close()
            self.assertEqual(len(calls),1)
    def test_nonstop_and_wrong_model_are_not_complete(self):
        for body in (response('length'),response(model='another-model')):
            with tempfile.TemporaryDirectory() as d:
                ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(lambda req:httpx.Response(200,json=body)))
                with self.assertRaises(Exception):ledger.invoke(entry()['payload']['messages'])
                state=json.loads((Path(d)/'norm-0001/state.json').read_text())
                self.assertEqual(state['status'],'FAILED');ledger.close()
    def test_changed_message_is_blocked_before_request(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[]
            def handler(req):calls.append(1);return httpx.Response(200,json=response())
            ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(handler))
            with self.assertRaises(Exception):ledger.invoke([{'role':'user','content':'changed'}])
            self.assertFalse(calls);ledger.close()
    def test_network_failure_records_uncertain_and_no_retry(self):
        with tempfile.TemporaryDirectory() as d:
            calls=[]
            def handler(req):calls.append(1);raise httpx.ConnectError('mock connection lost',request=req)
            ledger=FrozenLedger(Path(d),[entry()],'mock-not-secret',httpx.MockTransport(handler))
            with self.assertRaises(Exception):ledger.invoke(entry()['payload']['messages'])
            self.assertEqual(len(calls),1);ledger.close()
            state=json.loads((Path(d)/'norm-0001/state.json').read_text());self.assertEqual(state['status'],'FAILED')
            self.assertTrue(state['billing_unknown'])
if __name__=='__main__':unittest.main()
