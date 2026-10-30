"""Offline regression checks for the Fully-only semantic Prompt migration."""
import ast, contextlib, importlib.util, json, os, random, tempfile, types, unittest
from pathlib import Path
import httpx
import normalize_fully as n

class Tests(unittest.TestCase):
    def test_fully_rules_match_unmodified_official_main(self):
        root = n.ROOT
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            p=Path(tmp); gold={'g':{'TDMs':[{'Task':'T','Dataset':'D','Metric':'M','Result':'0'}]}}
            raw={'p.pdf':{'output':json.dumps([
                {'Task':'T','Dataset':'D','Metric':'M','Result':'01.00'},
                {'Task':'Alias','Dataset':'Unknown','Metric':'Quoted','Result':'2.0'},
                {'Task':'Alias','Dataset':'D','Metric':'NoneLabel','Result':'3.00'}]),'source_documents':[{'content':'untouched'}]}}
            answers={'Alias':'T','Unknown':'Unknown','Quoted':'"M"','NoneLabel':'None'}
            for f,v in {'config.json':{'is_few_shot':False,'model_type':'gpt4-turbo-128k'},'gold.json':gold,'output.json':raw,'prompts.json':{'normalization-system-prompt':'test'}}.items():
                (p/f).write_text(json.dumps(v),encoding='utf8')
            requests=[]
            class Prompt:
                def __init__(self,*a):self.prompt_template=self
                def invoke(self,x):return x
            def invoke(x):
                requests.append(x['input']);return types.SimpleNamespace(content=answers[x['input']])
            @contextlib.contextmanager
            def cb():yield types.SimpleNamespace(prompt_tokens=0,completion_tokens=0,total_cost=0)
            official=n.REPO/'tdm_llm_normalization.py'
            fn=next(x for x in ast.parse(official.read_text('utf8')).body if isinstance(x,ast.FunctionDef) and x.name=='main')
            ns={'torch':types.SimpleNamespace(manual_seed=lambda x:None),'random':random,'json':json,'os':os,
                'utils':types.SimpleNamespace(read_json=n.load,llm_init_langchain=lambda *a,**k:types.SimpleNamespace(invoke=invoke)),
                'NormalizationPrompt':Prompt,'get_openai_callback':cb,'tqdm':types.SimpleNamespace(tqdm=lambda x,**k:x)}
            exec(compile(ast.Module(body=[fn],type_ignores=[]),str(official),'exec'),ns)
            ns['main'](types.SimpleNamespace(seed=0,tdm_output_path=str(p)+'/',gold_tdm_path=str(p/'gold.json'),prompt_file=str(p/'prompts.json'),max_new_tokens=None))
            actual_calls=[]
            def call(i,k,v):actual_calls.append(v);return answers[v]
            actual=n.normalize_rows(json.loads(raw['p.pdf']['output']),{'Task':{'T'},'Dataset':{'D'},'Metric':{'M'}},call)
            expected=n.load(p/'normalization/normalized_output.json')['p.pdf']['normalized_output']
            self.assertEqual(actual,expected);self.assertEqual(actual_calls,requests)
            self.assertEqual(actual_calls.count('Alias'),2)
            self.assertIsNone(actual[1]['Dataset']);self.assertIsNone(actual[1]['Metric']);self.assertIsNone(actual[2]['Metric'])
            self.assertEqual([r['Result'] for r in actual],['01.00','2.0','3.00'])

    def test_exact_user_template_and_no_extra_context(self):
        msg=n.messages('S',"{'A'}",'Alias')
        self.assertEqual(msg,[{'role':'system','content':'S'},{'role':'user','content':"\n\nItem list: {'A'}\n\nInput: Alias\n\nAnswer: "}])

    def test_migration_only_fully_key_and_none_fallback(self):
        before=n.load(n.ROOT/'prompts_original.json');after=n.load(n.ROOT/'prompts_fully_semantic_v1.json')
        self.assertEqual({k for k in before if before[k]!=after[k]},{'normalization-system-prompt'})
        added=n.load(n.ROOT/'prompt_migration.json')['fully_addition']
        self.assertEqual(after['normalization-system-prompt'],before['normalization-system-prompt']+added)
        self.assertIn('output None',added);self.assertNotIn('output the original input entity',added)
        for key in ('masked-normalization-system-prompt','leaderboard-normalization-system-prompt'):
            self.assertEqual(before.get(key),after.get(key))

    def test_all_extractions_and_candidate_order_unchanged(self):
        m=n.load(n.ROOT/'experiment_manifest.json')
        self.assertEqual(m['papers'],5);self.assertEqual(m['gold_records'],28)
        self.assertEqual(m['new_extraction_requests'],0);self.assertEqual(m['normalization_requests'],144)
        for arm,meta in m['arms'].items():
            self.assertEqual(n.digest(n.ROOT/arm/'merged/output.json'),meta['source_sha256'])
            self.assertEqual(n.digest(n.ROOT/'candidate_sets.json'),meta['candidate_sets_sha256'])
            for row in n.load(n.ROOT/arm/'request_manifest.json'):
                self.assertNotIn('Result',row['field'])

    def test_wire_no_output_cap_and_resume_no_resend(self):
        calls=[]
        def handler(request):
            calls.append(json.loads(request.content));return httpx.Response(200,json={'model':'deepseek-flash','choices':[{'finish_reason':'stop','message':{'content':'T'}}]})
        with tempfile.TemporaryDirectory(dir=n.ROOT) as tmp,httpx.Client(transport=httpx.MockTransport(handler)) as c:
            for _ in range(2):n.request(c,Path(tmp)/'call',n.messages('s',"{'T'}",'alias'),'synthetic',False)
        self.assertEqual(len(calls),1)
        self.assertEqual(set(calls[0]),{'model','messages','thinking','reasoning_effort','stream'})

    def test_failed_request_never_auto_resends(self):
        for mode in ('timeout','http','nonstop'):
            calls=[]
            def handler(request):
                calls.append(1)
                if mode=='timeout':raise httpx.ReadTimeout('synthetic',request=request)
                if mode=='http':return httpx.Response(500,json={'error':'synthetic'})
                return httpx.Response(200,json={'model':'deepseek-flash','choices':[{'finish_reason':'length','message':{'content':'T'}}]})
            with tempfile.TemporaryDirectory(dir=n.ROOT) as tmp,httpx.Client(transport=httpx.MockTransport(handler)) as c:
                for _ in range(2):
                    with self.assertRaises((n.ServiceStop,n.FormatStop)):n.request(c,Path(tmp)/'call',[], 'synthetic',False)
            self.assertEqual(len(calls),1)

if __name__=='__main__':
    def guard(event,args):
        if event in ('socket.connect','socket.getaddrinfo'):raise RuntimeError('Tests prohibit real network')
        if event=='open' and isinstance(args[0],str) and args[0].lower().endswith('.env'):raise RuntimeError('Tests prohibit credentials')
    import sys
    sys.addaudithook(guard)
    unittest.main(verbosity=2)
