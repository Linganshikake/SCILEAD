"""Local tokenizer JSON only. No transformers, torch, models, downloads or network."""
import ast, json, hashlib
from pathlib import Path
from tokenizers import Tokenizer, AddedToken
import tokenizers
O=Path(__file__).resolve().parent;P=Path(r'D:\C++\SCILEAD\pilot');S=P/'autodl_setup/20261021/stage'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
prompts=read(S/'source/prompts.json')
tree=ast.parse((S/'source/prompting.py').read_text(encoding='utf-8'))
branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and any(isinstance(c,ast.Constant) and c.value=='llama-3-instruct-70b' for c in n.test.comparators))
expr=next(n.value for n in branch.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='initial_template' for t in n.targets))
def ev(n):
    if isinstance(n,ast.Constant):return n.value
    if isinstance(n,ast.Name) and n.id=='system_prompt':return prompts['tdm-extraction-system-prompt']
    if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):return ev(n.left)+ev(n.right)
    raise ValueError('Unexpected template expression')
template=ev(expr);tp=P/'autodl_setup/20261021/authorized_model_small_files/llama3/tokenizer.json'
a=Tokenizer.from_file(str(tp));b=Tokenizer.from_file(str(tp));b.add_special_tokens([AddedToken('<pad>',special=True)])
result={'tokenizers_version':tokenizers.__version__,'runtime_tokenizers_version':'0.19.1','version_caveat':'Independent local tokenizer 0.15.2 recount, compared with archived actual 0.19.1 runtime observations; does not replace runtime evidence.','tokenizer_file':str(tp),'tokenizer_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'model_loaded':False,'network_used':False,'papers':{}}
for x in read(S/'data/paper_index.json'):
    pid=x['paper_id'];docs=read(S/x['evidence_file'])[pid];prompt=template.format(question=prompts['query'],context='\n\n'.join(d['content'] for d in docs))
    result['papers'][pid]={'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'before_author_pad':len(a.encode(prompt,add_special_tokens=False).ids),'after_author_pad':len(b.encode(prompt,add_special_tokens=False).ids),'pad_literal_occurrences':prompt.count('<pad>')}
(O/'tokenizer_recount.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'papers':len(result['papers']),'long':result['papers']['1912.08777.pdf'],'pad_case':result['papers']['1811.05021.pdf']}))
