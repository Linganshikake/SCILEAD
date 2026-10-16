import ast,collections,random,shutil,subprocess
from common import *

def audit_partially():
    from prompting import NormalizationPrompt
    pc=read(PARTIAL/'config.json');boards=read(pc['leaderboards_path']);stage1=read(PARTIAL/'stage1/normalized_output.json');stage2=read(PARTIAL/'stage2/leaderboard_normalized_output.json')
    candidates={'('+', '.join(b[k] for k in ('Task','Dataset','Metric'))+')' for b in boards};assert len(candidates)==27
    serial='{'+', '.join(candidates)+'}';prompt=NormalizationPrompt(read(REPO/'prompts.json')['leaderboard-normalization-system-prompt'],'gpt4-turbo-128k')
    events=[read(p) for p in sorted((PARTIAL/'stage2/events').glob('*.json'))];counts=collections.Counter();calls=[]
    assert len(events)==284
    for e in events:
        old=stage1[e['paper']]['normalized_output'][e['record']-1];new=stage2[e['paper']]['normalized_output'][e['record']-1]
        assert e['original']==old and e['normalized']==new and set(e['candidate_order'])==candidates and e['candidate_serialized']==serial
        counts[e['branch']]+=1
        if 'call' not in e:
            assert new==old
            if e['branch']=='null_skipped':assert any(old[k] is None for k in ('Task','Dataset','Metric'))
            else:assert '('+', '.join(old[k] for k in ('Task','Dataset','Metric'))+')' in candidates
            continue
        folder=PARTIAL/'stage2/api_calls'/f"{e['call']:04d}"
        req=read(folder/'request.json');resp=read(folder/'response.json');state=read(folder/'state.json');expected=read(folder/'expected.json')
        item='('+', '.join(old[k] for k in ('Task','Dataset','Metric'))+')'
        messages=wire(prompt.prompt_template.invoke({'items':serial,'input':item}).to_messages())
        assert req['messages']==messages==expected['messages'] and expected['original']==item
        assert state['status']=='COMPLETE' and state['http_status']==200 and state['finish_reason']=='stop' and state['returned_model']==MODEL
        answer=resp['choices'][0]['message']['content'];assert answer==e['raw_answer']==state['raw_answer'] and digest(resp)==state['response_sha256']
        if e['branch']=='tuple_mapped':
            assert answer in candidates
            assert [new[k] for k in ('Task','Dataset','Metric')]==answer[1:-1].split(', ')[:3]
        else:assert e['branch']=='unmatched_preserved' and answer not in candidates and answer==item and new==old
        assert new['Result']==old['Result'];calls.append(e['call'])
    assert sorted(calls)==list(range(1,205))
    assert dict(counts)=={'unmatched_preserved':189,'tuple_mapped':15,'null_skipped':68,'exact_tuple':12}
    result={'status':'PASS','events':len(events),'calls_audited':len(calls),'branches':dict(counts),'all27_candidates_complete':True,'official_messages_exact':True,'echoes_are_true_response_content':True,'all_mappings_exact_candidate_members':True,'null_rows_skipped':True,'new_api_calls':0,'partially_modified':False}
    save(TOP/'preflight_audit.json',result)
    (TOP/'preflight_audit.md').write_text('# Partially 衔接审计\n\n逐条核对全部 204 个实际请求和 284 个事件。原版 Prompt、system/user 角色、27 个完整候选、逐行输入与真实响应完全一致。189 次原样返回均来自保存的 HTTP 响应；15 次映射均为完整候选成员；68 条含 null 跳过，12 条精确匹配跳过。未发现适配错误，保留 Partially 结果，继续 Cold Start。审计未调用 API，也未更改旧文件。\n',encoding='utf-8')
    return result

def main():
    setup();assert RUN==TOP and os.environ.get('PYTHONHASHSEED')=='0';assert not (TOP/'freeze_before.json').exists()
    prior=read(PARTIAL/'freeze_before.json')
    for root,files in prior['directories'].items():
        assert set(files)=={str(p) for p in Path(root).rglob('*') if p.is_file()}
        for p,h in files.items():assert sha(p)==h
    for p,h in prior['sources_gold'].items():assert sha(p)==h
    frozen={'directories':{str(d):{str(p):sha(p) for p in d.rglob('*') if p.is_file()} for d in (BASE,CS,PARTIAL,LB)},'sources_gold':prior['sources_gold'],'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()}}
    save(TOP/'freeze_before.json',frozen);audit=audit_partially()
    conf=read(PARTIAL/'config.json');raw=read(BASE/'merged/output.json');gold=read(conf['gold_path']);boards=read(conf['leaderboards_path'])
    assert len(raw)==43 and sum(len(json.loads(x['output'])) for x in raw.values())==284 and sum(len(x['TDMs']) for x in gold.values())==295 and len(boards)==27
    assert list(raw)==read(PARTIAL/'paper_order.json')['papers'] and sha(BASE/'merged/output.json')==conf['input_sha256']
    (TOP/'references').mkdir();shutil.copyfile(PARTIAL/'masking/partially_masked_leaderboards.json',TOP/'references/masked10.json');assert len(read(TOP/'references/masked10.json'))==10
    # Execute only the official __main__ argparse block with main replaced by capture.
    source=(REPO/'tdm_llm_masked_normalization.py').read_text(encoding='utf-8');tree=ast.parse(source);block=tree.body[-1];assert isinstance(block,ast.If)
    import argparse
    import tdm_llm_masked_normalization as official
    orders={};start=time.time()
    for run_id,seed in [('order_default',None),('order_0','0'),('order_42','42')]:
        captured={};argv=sys.argv
        sys.argv=['official','--gold_tdm_file','unused','--gold_leaderboard_file','unused','--tdm_config_file','unused','--tdm_output_file','unused','--normalization_output_path','unused','--cold_start']+(['--cold_start_seed',seed] if seed is not None else [])
        try:exec(compile(ast.Module(body=block.body,type_ignores=[]),str(REPO/'tdm_llm_masked_normalization.py'),'exec'),{'argparse':argparse,'main':lambda a:captured.update(vars(a))})
        finally:sys.argv=argv
        assert captured['cold_start_seed']==seed and (seed is None or type(captured['cold_start_seed']) is str)
        order=list(raw)
        if seed is not None:random.seed(seed);order=random.sample(list(raw),len(raw))
        assert len(set(order))==43 and set(order)==set(raw);out=TOP/run_id;out.mkdir();(out/'work').mkdir();(out/'reproducibility').mkdir()
        labels=official.sample_tdms(boards,gold,0,out.as_posix()+'/',True,'initialization/')
        assert labels=={k:set() for k in ('Task','Dataset','Metric')}
        save(out/'initialization/initial_labels.json',labels_state(labels))
        save(out/'paper_order.json',{'policy':'frozen_output_key_order' if seed is None else 'official random.seed + random.sample','cold_start_seed':seed,'cold_start_seed_type':type(seed).__name__,'model_seed':0,'model_seed_type':'int','python_hash_seed':'0','papers':order,'frozen_raw_key_order':list(raw),'official_cli_parsed':captured})
        runconf={**conf,'run_id':run_id,'cold_start':True,'cold_start_seed':seed,'cold_start_seed_type':type(seed).__name__,'input_path':str(BASE/'merged/output.json'),'paper_order':str(out/'paper_order.json'),'started_epoch':start,'masked10_path':str(TOP/'references/masked10.json'),'masked10_sha256':sha(TOP/'references/masked10.json')}
        save(out/'config.json',runconf);save(out/'work/official_config.json',{'model_type':'gpt4-turbo-128k'});orders[run_id]={'paper_order_sha256':sha(out/'paper_order.json'),'seed':seed,'seed_type':type(seed).__name__}
    commit=subprocess.run(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,text=True,capture_output=True,check=True).stdout.strip();assert commit==conf['commit']
    save(TOP/'experiment_manifest.json',{'status':'PREPARED','started_epoch':start,'commit':commit,'papers':43,'predictions':284,'gold_records':295,'gold_boards':27,'masked_boards':10,'raw_input_path':str(BASE/'merged/output.json'),'raw_sha256':sha(BASE/'merged/output.json'),'masked10_source':str(PARTIAL/'masking/partially_masked_leaderboards.json'),'masked10_sha256':sha(TOP/'references/masked10.json'),'orders':orders,'model':MODEL,'generation_seed':0,'output_caps':'OMITTED; differs from author stage1=15 and stage2=100 defaults','std_main_ddof':1,'std_secondary_ddof':0,'author_ddof':'UNCONFIRMED; checked official source and paper references','preflight':audit})
    verify();print(json.dumps({'audit':audit,'orders':orders,'frozen_files':sum(map(len,frozen['directories'].values()))}))
if __name__=='__main__':main()
