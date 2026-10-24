import json
import tempfile
import unittest
from pathlib import Path
import httpx
from run_trial import validate, one_request, MODEL

class TrialTests(unittest.TestCase):
    def response(self, text='[]', finish='stop', model=MODEL):
        return {'model':model,'choices':[{'finish_reason':finish,'message':{'content':text}}]}
    def test_array_and_string_result(self):
        row={'Task':'T','Dataset':'D','Metric':'M','Result':'1.00'}
        self.assertEqual(validate(self.response(json.dumps([row])), True),[row])
    def test_invalid_payloads_stop(self):
        for text in ['```json\n[]\n```','[','{}','[{"Task":"T"}]','[{"Task":"T","Dataset":"D","Metric":"M","Result":1}]']:
            with self.subTest(text=text),self.assertRaises(ValueError): validate(self.response(text),True)
    def test_wrong_model_and_truncation_stop(self):
        for r in [self.response(finish='length'),self.response(model='other')]:
            with self.assertRaises(ValueError):validate(r,True)
    def test_normalization_not_stripped(self):
        self.assertEqual(validate(self.response(' F1\n'),False),' F1\n')
    def test_failed_request_not_repeated(self):
        calls=[]
        def handler(req):
            calls.append(req)
            return httpx.Response(500,json={'error':{'code':'get_channel_failed'}})
        with tempfile.TemporaryDirectory() as d,httpx.Client(transport=httpx.MockTransport(handler)) as client:
            p=Path(d)
            with self.assertRaises(RuntimeError):one_request(client,p,{},'test-key','https://9527.codes/v1/chat/completions')
            with self.assertRaises(FileExistsError):one_request(client,p,{},'test-key','https://9527.codes/v1/chat/completions')
            self.assertEqual(len(calls),1)
            self.assertEqual(json.loads((p/'state.json').read_text())['status'],'HTTP_ERROR')

if __name__=='__main__':unittest.main()
