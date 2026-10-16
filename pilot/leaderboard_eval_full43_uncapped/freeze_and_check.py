import collections,importlib.metadata,subprocess
from common import *
def no_duplicates(p):
    def hook(pairs):
        d={}
        for k,v in pairs:
            assert k not in d,('duplicate JSON key',str(p),k);d[k]=v
        return d
    return json.loads(p.read_text(encoding='utf-8'),object_pairs_hook=hook)
def main():
    boundary();assert not (RUN/'freeze_before.json').exists(),'Snapshot already frozen'
    for path,h in read(BASE/'file_integrity_sha256.json').items():assert sha(BASE/path)==h
    env=read(BASE/'environment.json');v=read(BASE/'verification.json');gold=no_duplicates(GOLD);tdm=no_duplicates(TDM);norm=no_duplicates(NORMALIZED)
    for path,h in env['source_sha256'].items():assert sha(path)==h
    assert sha(TDM)==read(BASE/'manifest.json')['gold_sha256']
    assert env['dependencies']=={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,text=True).strip();assert commit==env['git_commit']=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    assert len(norm)==len(tdm)==43 and set(norm)==set(tdm);assert sum(len(x['TDMs']) for x in tdm.values())==295
    for p,x in norm.items():
        assert isinstance(x['normalized_output'],list) and 'source_documents' in x
        for t in x['normalized_output']:assert set(t)=={'Task','Dataset','Metric','Result'} and isinstance(t['Result'],str) and all(t[k] is None or isinstance(t[k],str) for k in ('Task','Dataset','Metric'))
    ev=read(BASE/'evaluation/eval_results.json');p=ev['Exact Match Precision'];r=ev['Exact Match Recall'];f1=2*p*r/(p+r);assert abs(f1-.4215783575665092)<1e-12
    manifest=read(BASE/'manifest.json');wire_count=0
    for row in manifest['papers']:
        for key in ('extraction_dir','normalization_dir'):
            for f in Path(row[key]).glob('api_calls/*/request.json'):
                q=read(f);assert set(q)=={'messages','model','n','seed','stream','temperature'};assert q['model']=='gpt-4.1-2025-04-14' and q['temperature']==0 and q['seed']==0;wire_count+=1
    assert wire_count==585
    groups=collections.defaultdict(dict);duplicate_tdms=[]
    for paper,x in tdm.items():
        for t in x['TDMs']:
            k=tuple(t[z] for z in ('Task','Dataset','Metric'))
            if paper in groups[k]:duplicate_tdms.append({'paper':paper,'tdm':k})
            groups[k][paper]=t['Result']
    keys=[tuple(x[k] for k in ('Task','Dataset','Metric')) for x in gold];assert len(gold)==len(set(keys))==27
    boards=[]
    for i,(key,x) in enumerate(zip(keys,gold),1):
        assert len(x['Leaderboard'])>=3 and set(x['Leaderboard'])<=set(norm)
        assert x['Leaderboard']==groups[key]
        boards.append({'index':i,'tdm':key,'gold_papers':len(x['Leaderboard']),'paper_ids':list(x['Leaderboard']),'gold_results':x['Leaderboard']})
    sources={str(p):sha(p) for p in REPO.iterdir() if p.is_file() and (p.suffix in ('.py','.json','.md') or p.name=='requirements.txt')}
    sources.update({str(GOLD):sha(GOLD),str(TDM):sha(TDM),str(RUN.parent/'experiment_settings.json'):sha(RUN.parent/'experiment_settings.json')})
    snapshot={'all_baseline_files':{str(p):sha(p) for p in BASE.rglob('*') if p.is_file()},'sources_and_gold':sources,'baseline_tdmr_f1':f1,'git_commit':commit,'model':'gpt-4.1-2025-04-14','baseline_selected_wire_requests':wire_count,'new_llm_requests':0,'dependencies':env['dependencies']}
    save(RUN/'freeze_before.json',snapshot)
    audit={'gold_leaderboards':27,'entries':sum(len(x['Leaderboard']) for x in gold),'mean_papers':sum(len(x['Leaderboard']) for x in gold)/27,'minimum_papers':min(len(x['Leaderboard']) for x in gold),'normalized_papers':43,'normalized_rows':sum(len(x['normalized_output']) for x in norm.values()),'tdm_gold_rows':295,'actual_unique_gold_tdms':len(groups),'paper_reported_unique_tdms':138,'groups_with_at_least_3_papers':sum(len(x)>=3 for x in groups.values()),'extra_3plus_groups_not_in_leaderboard_file':[{'tdm':k,'papers':list(x),'results':x} for k,x in groups.items() if len(x)>=3 and k not in keys],'duplicate_json_keys':False,'duplicate_gold_tdm_per_paper':duplicate_tdms,'all_board_entries_match_tdm_annotations':True,'paper_ids_all_in_normalized_output':True,'boards':boards,'scope_decision':'Use supplied 27 leaderboards unchanged. Matches paper count and >=3 threshold; cannot independently prove identical historical version from paper alone. Do not regenerate 33 leaderboards.'}
    save(RUN/'input_audit.json',audit);verify_frozen();print(json.dumps({k:v for k,v in audit.items() if k not in ('boards','extra_3plus_groups_not_in_leaderboard_file')},ensure_ascii=False))
if __name__=='__main__':main()
