import ast,shutil,subprocess,time
from cs_common import *
def main():
    setup();assert not (RUN/'freeze_before.json').exists()
    for directory,inventory in [(BASE,'file_integrity_sha256.json'),(LB,'artifact_sha256.json')]:
        for p,h in read(directory/inventory).items():assert sha(directory/p)==h,p
    manifest=read(BASE/'manifest.json');gold_path=Path(manifest['gold_path']);gold=read(gold_path);raw=read(BASE/'merged/output.json');old=read(BASE/'merged/normalized_output.json');boards=read(LB/'official/invocation.json');bg=Path(boards['gold_leaderboards_file'])
    assert len(raw)==len(gold)==43 and set(raw)==set(gold)==set(old);assert sum(len(x['TDMs']) for x in gold.values())==295
    labels={k:set(t[k] for x in gold.values() for t in x['TDMs']) for k in ('Task','Dataset','Metric')};assert {k:len(v) for k,v in labels.items()}=={'Task':23,'Dataset':71,'Metric':26}
    raw_count=0;cs=0
    for p,x in raw.items():
        rs=json.loads(x['output']);raw_count+=len(rs);assert len(rs)==len(old[p]['normalized_output'])
        for row in rs:cs+=sum(row[k] not in labels[k] for k in labels)
    assert len(read(bg))==27 and sum(len(b['Leaderboard']) for b in read(bg))==140
    source_files=[p for p in REPO.iterdir() if p.is_file() and (p.suffix in ('.py','.md','.json') or p.name=='requirements.txt')]+[gold_path,bg,RUN.parent/'experiment_settings.json']
    for p,h in read(BASE/'environment.json')['source_sha256'].items():assert sha(p)==h
    commit=subprocess.check_output(['git','-c','safe.directory='+REPO.as_posix(),'rev-parse','HEAD'],cwd=REPO,text=True).strip();assert commit=='8bf74b0a830feb7035c6166dce3394dc344ae532'
    save(RUN/'freeze_before.json',{'directories':{str(d):{str(p):sha(p) for p in d.rglob('*') if p.is_file()} for d in (BASE,LB)},'sources_gold':{str(p):sha(p) for p in source_files},'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'commit':commit})
    for folder in ('work','merged'):
        dest=RUN/folder/'output.json';dest.parent.mkdir(exist_ok=True);shutil.copy2(BASE/'merged/output.json',dest);assert sha(dest)==sha(BASE/'merged/output.json')
    save(RUN/'config.json',{'model':MODEL,'revision':REV,'code_repository':CODE,'code_revision':CODE_REV,'device':'cpu','dtype':'float32','python_hash_seed':0,'seed':0,'threads':4,'gold_path':str(gold_path),'gold_leaderboards_path':str(bg),'input_path':str(BASE/'merged/output.json'),'input_sha256':sha(BASE/'merged/output.json'),'papers':43,'gold_tdmrs':295,'raw_records':raw_count,'expected_cs_fields':cs,'expected_exact_fields':raw_count*3-cs,'candidate_counts':{k:len(v) for k,v in labels.items()},'new_llm_requests':0,'started_epoch':time.time(),'memory_before':memory(),'disk_free':shutil.disk_usage(ROOT).free,'algorithm':'unchanged official main; adapter limited to fixed local model CPU/FP32 and logging/checkpoints'})
    code_audit={}
    for name in ('config.py','modeling.py'):
        tree=ast.parse((CODE_PATH/name).read_text(encoding='utf-8'));code_audit[name]={'sha256':sha(CODE_PATH/name),'imports':sorted({n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module}),'direct_eval_exec_open_import_calls':[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('eval','exec','open','__import__')]};assert not code_audit[name]['direct_eval_exec_open_import_calls']
    save(RUN/'reproducibility/custom_code_review.json',{'auto_map':read(SNAPSHOT/'config.json')['auto_map'],'actual_import_files':code_audit,'review':'Inspected imports, top-level statements, model/config definitions and I/O patterns. Actual dependencies are torch, transformers, standard library, and relative config; no network/shell/config-reading operations in selected implementation.','unmodified_model_modules':read(SNAPSHOT/'modules.json'),'pooling':read(SNAPSHOT/'1_Pooling/config.json')})
    info=read(RUN/'reproducibility/bilingual-embedding-large-repository.json');expected=next(s['lfs']['sha256'] for s in info['siblings'] if s['rfilename']=='model.safetensors');assert sha(SNAPSHOT/'model.safetensors')==expected
    save(RUN/'model_manifest.json',{'model':MODEL,'weight_revision':REV,'code_repository':CODE,'code_revision':CODE_REV,'local_snapshot':str(SNAPSHOT),'model_files_sha256':{str(p.relative_to(SNAPSHOT)):sha(p) for p in SNAPSHOT.rglob('*') if p.is_file()},'code_files_sha256':{n:sha(CODE_PATH/n) for n in ('config.py','modeling.py')},'weight_lfs_sha256':expected,'no_alternate_weight_format_downloaded':True})
    verify();print(json.dumps(read(RUN/'config.json'),ensure_ascii=False))
if __name__=='__main__':main()
