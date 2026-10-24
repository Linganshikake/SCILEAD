from pathlib import Path
import json,hashlib,time
R=Path(__file__).resolve().parents[1];OLD=Path(r'D:\C++\SCILEAD\pilot\full43_cs')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    started=time.monotonic();m=json.loads((OLD/'model_manifest.json').read_text(encoding='utf-8'));snapshot=Path(m['local_snapshot']);files=[]
    for name,expected in m['model_files_sha256'].items():
        p=snapshot/name;actual=sha(p);assert actual==expected
        files.append({'name':name,'bytes':p.stat().st_size,'sha256':actual})
    result={'status':'LOCAL_OFFICIAL_MODEL_FILES_VERIFIED','model':m['model'],'revision':m['weight_revision'],'code_revision':m['code_revision'],'files':files,'prior_cpu_forward_validation':m['actual_runtime'],'server_actual_cs_inference_validated':False,'server_weight_migration_done':False,'new_model_loading_or_embedding_calls':0,'persistent_embedding_cache_found':False,'persistent_cache_search_scope':'full43_cs/*.npy, *.npz, *.pkl recursive','prior_prediction_mappings_not_reusable_as_llama_predictions':True,'seconds':time.monotonic()-started}
    candidates=[str(p) for pattern in ['*.npy','*.npz','*.pkl'] for p in OLD.rglob(pattern)]
    result['persistent_embedding_cache_candidates']=candidates;result['persistent_embedding_cache_found']=bool(candidates)
    (R/'diagnostics/cs_readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':result['status'],'verified_files':len(files),'bytes':sum(x['bytes'] for x in files),'new_embeddings':0,'seconds':result['seconds']}))
if __name__=='__main__':main()
