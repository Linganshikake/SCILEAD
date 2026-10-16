from common import *
import collections,csv,io,zipfile,shutil,math

FIELDS=('Task','Dataset','Metric')
class Pairs(list):pass
def strict_json(content):
    duplicates=[]
    obj=json.loads(content,object_pairs_hook=Pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON: '+x)))
    def walk(x,path):
        if isinstance(x,Pairs):
            out={}
            for k,v in x:
                val=walk(v,path+'/'+k.replace('~','~0').replace('/','~1'))
                if k in out:duplicates.append({'path':path,'key':k,'previous_value':out[k],'new_value':val})
                out[k]=val
            return out
        if isinstance(x,list):return [walk(v,path+'/'+str(i)) for i,v in enumerate(x)]
        return x
    return walk(obj,''),duplicates
def tdm(x):return tuple(x[k] for k in FIELDS)
def rows_of(gold):return [{'paper_id':p,'record_index':i,**r} for p,v in gold.items() for i,r in enumerate(v['TDMs'],1)]
def profile_annotations(gold):
    rows=rows_of(gold);groups=collections.defaultdict(list);paper_tdm=collections.defaultdict(list);invalid=[]
    for r in rows:
        if not all(isinstance(r.get(k),str) and r[k]!='' for k in FIELDS) or 'Result' not in r:invalid.append(r);continue
        groups[tdm(r)].append(r);paper_tdm[(r['paper_id'],tdm(r))].append(r)
    multiple=[{'paper_id':p,'tdm':list(k),'rows':v,'conflicting_results':any(x['Result']!=v[0]['Result'] for x in v[1:])} for (p,k),v in paper_tdm.items() if len(v)>1]
    duplicate_records=[]
    counter=collections.Counter((r['paper_id'],tdm(r),json.dumps(r['Result'],ensure_ascii=False)) for r in rows)
    for (p,k,res),n in counter.items():
        if n>1:duplicate_records.append({'paper_id':p,'tdm':list(k),'Result_serialized':res,'count':n})
    sizes={k:len({r['paper_id'] for r in v}) for k,v in groups.items()}
    summary={'papers':len(gold),'records':len(rows),'unique_tdm':len(groups),'candidate_counts':{k:len({r[k] for r in rows}) for k in FIELDS},'label_sets':{k:sorted({r[k] for r in rows}) for k in FIELDS},'groups_ge2':sum(n>=2 for n in sizes.values()),'groups_ge3':sum(n>=3 for n in sizes.values()),'distinct_paper_size_histogram':dict(sorted(collections.Counter(sizes.values()).items())),'multiple_rows_same_paper_tdm':multiple,'conflicting_paper_tdm_count':sum(x['conflicting_results'] for x in multiple),'duplicate_records':duplicate_records,'invalid_rows':invalid}
    return summary,groups
def profile_boards(boards,gold,groups):
    seen={};dups=[];invalid=[];matches=[];unknown=[];keys=[]
    for i,b in enumerate(boards,1):
        if not all(isinstance(b.get(k),str) and b[k]!='' for k in FIELDS) or not isinstance(b.get('Leaderboard'),dict):invalid.append({'index':i,'board':b});continue
        key=tdm(b);keys.append(key)
        if key in seen:dups.append({'tdm':list(key),'first_index':seen[key],'duplicate_index':i})
        seen[key]=i
        for p,value in b['Leaderboard'].items():
            if p not in gold:unknown.append({'board_index':i,'tdm':list(key),'paper_id':p})
            rr=[r for r in groups.get(key,[]) if r['paper_id']==p]
            if not any(r['Result']==value for r in rr):matches.append({'board_index':i,'tdm':list(key),'paper_id':p,'board_result':value,'gold_exact_tdm_rows':rr,'other_gold_rows_for_paper':[r for r in rows_of(gold) if r['paper_id']==p] if not rr else []})
    return {'boards':len(boards),'unique_tdm':len(set(keys)),'records':sum(len(x.get('Leaderboard',{})) for x in boards),'different_papers':len({p for x in boards for p in x.get('Leaderboard',{})}),'minimum_distinct_papers':min((len(x.get('Leaderboard',{})) for x in boards),default=0),'all_papers_in_frozen_gold':not unknown,'unknown_papers':unknown,'duplicate_boards':dups,'invalid_boards':invalid,'paper_tdm_result_mismatches':matches}
def annotation_diff(a,b):
    def counter(g):return collections.Counter((p,*tdm(r),json.dumps(r['Result'],ensure_ascii=False)) for p,v in g.items() for r in v['TDMs'])
    ca,cb=counter(a),counter(b)
    def describe(c):return [{'paper_id':k[0],'Task':k[1],'Dataset':k[2],'Metric':k[3],'Result_serialized':k[4],'count':n} for k,n in c.items()]
    pa,_=profile_annotations(a);pb,_=profile_annotations(b)
    return {'paper_ids_removed':sorted(set(a)-set(b)),'paper_ids_added':sorted(set(b)-set(a)),'records_removed':describe(ca-cb),'records_added':describe(cb-ca),'labels_removed':{k:sorted(set(pa['label_sets'][k])-set(pb['label_sets'][k])) for k in FIELDS},'labels_added':{k:sorted(set(pb['label_sets'][k])-set(pa['label_sets'][k])) for k in FIELDS},'equal_structured_records':ca==cb,'before_summary':{k:pa[k] for k in ('papers','records','unique_tdm','candidate_counts')},'after_summary':{k:pb[k] for k in ('papers','records','unique_tdm','candidate_counts')}}
def kind(obj):
    if isinstance(obj,list) and obj and all(isinstance(x,dict) and set(FIELDS).issubset(x) and isinstance(x.get('Leaderboard'),dict) for x in obj):return 'leaderboards'
    if isinstance(obj,dict) and obj and all(isinstance(x,dict) and isinstance(x.get('TDMs'),list) for x in obj.values()):return 'annotations'
    return 'other_json'
def main():
    setup();m=read(PILOT/'full43_fewshot_both_prompts/input_manifest.json');gp=Path(m['gold_path']);bp=Path(m['gold_leaderboards_path']);gold,gdup=strict_json(gp.read_text(encoding='utf-8-sig'));boards,bdup=strict_json(bp.read_text(encoding='utf-8-sig'))
    gs,groups=profile_annotations(gold);bs=profile_boards(boards,gold,groups)
    frozen={'gold_path':str(gp),'gold_sha256':sha(gp),'boards_path':str(bp),'boards_sha256':sha(bp),'annotations':gs,'annotations_duplicate_json_keys':gdup,'provided_boards':bs,'boards_duplicate_json_keys':bdup}
    save(ROOT/'verified_inputs/frozen_reference_manifest.json',{'scope':'Verified frozen reference only; not a threshold2 author artifact','gold_path':str(gp),'gold_sha256':sha(gp),'threshold3_path':str(bp),'threshold3_sha256':sha(bp)})
    for p in (gp,bp,gp.parent/'README.md',gp.parent/'tdm_annotations.tsv'):shutil.copyfile(p,ROOT/'verified_inputs'/('frozen_'+p.name))
    diagnostic=[]
    for k,rr in groups.items():
        papers=sorted({r['paper_id'] for r in rr})
        if len(papers)>=2:diagnostic.append({'tdm':list(k),'distinct_paper_count':len(papers),'paper_ids':papers,'raw_rows':rr,'formal_scoring_allowed':False})
    save(ROOT/'diagnostics/current_gold_ge2_NOT_FOR_SCORING.json',{'status':'DIAGNOSTIC_ONLY_NOT_AUTHOR_THRESHOLD2','no_result_selection_or_scaling':True,'groups':diagnostic})
    bmap={tdm(x):x for x in boards};missing_ge3=[{'tdm':list(k),'distinct_papers':len({r['paper_id'] for r in rr}),'rows':rr} for k,rr in groups.items() if len({r['paper_id'] for r in rr})>=3 and k not in bmap]
    shared_diffs=[]
    for k,b in bmap.items():
        rr=groups.get(k,[]);member={r['paper_id'] for r in rr};provided=set(b['Leaderboard'])
        differences={'tdm':list(k),'annotation_papers_absent_from_board':sorted(member-provided),'board_papers_absent_from_exact_annotation_tdm':sorted(provided-member),'value_mismatches':[x for x in bs['paper_tdm_result_mismatches'] if tuple(x['tdm'])==k]}
        if any(differences[x] for x in ('annotation_papers_absent_from_board','board_papers_absent_from_exact_annotation_tdm','value_mismatches')):shared_diffs.append(differences)
    sources=[];inventory=[];json_candidates=[];annotation_versions=[];fetchlogs=[]
    for file in ('official_fetch_log.json','official_attachment_fetch_log.json'):
        if (ROOT/file).exists():fetchlogs+=read(ROOT/file)
    def register(data,origin,size,source_url=None,readme=None,archive=None):
        entry={'origin':origin,'bytes':size,'sha256':hashlib.sha256(data).hexdigest(),'source_url':source_url,'archive':archive,'readme':readme}
        try:obj,duplicates=strict_json(data.decode('utf-8-sig'));entry.update(structure=kind(obj),duplicate_json_keys=duplicates)
        except Exception as e:entry.update(structure='invalid_json',error=str(e));sources.append(entry);return
        if entry['structure']=='annotations':
            stats,_=profile_annotations(obj);entry.update(profile=stats);entry['comparison_to_frozen']=annotation_diff(gold,obj);annotation_versions.append(entry)
        elif entry['structure']=='leaderboards':
            entry['profile']=profile_boards(obj,gold,groups);entry['exactly_equal_frozen27']=obj==boards;entry['readiness_threshold2_structure']=entry['profile']['unique_tdm']==62 and entry['profile']['minimum_distinct_papers']>=2
            json_candidates.append(entry)
        sources.append(entry)
    for path in gp.parent.glob('*.json'):register(path.read_bytes(),str(path),path.stat().st_size,readme=str(gp.parent/'README.md'))
    archives=[gp.parents[2]/'2024.emnlp-main.453.data.zip',gp.parents[2]/'2024.emnlp-main.453.software.zip']+sorted((ROOT/'downloads').glob('*.zip'))
    for archive in archives:
        if not zipfile.is_zipfile(archive):continue
        origin_url=next((x['url'] for x in fetchlogs if x.get('path')==str(archive)),None)
        with zipfile.ZipFile(archive) as z:
            entries=[];assert sum(x.file_size for x in z.infolist())<10*1024*1024
            for info in z.infolist():
                if info.is_dir():continue
                data=z.read(info);entries.append({'member':info.filename,'uncompressed_bytes':info.file_size,'sha256':hashlib.sha256(data).hexdigest()})
                if info.filename.endswith('.json'):register(data,str(archive)+'!'+info.filename,len(data),source_url=origin_url,archive=str(archive),readme='data/README.md' if info.filename.startswith('data/') else 'codes/README.md')
                if info.filename.endswith('README.md') and origin_url:
                    target=ROOT/'verified_inputs'/('official_'+archive.stem+'_'+Path(info.filename).name);target.write_bytes(data)
            inventory.append({'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'source_url':origin_url,'members':entries})
    with (gp.parent/'tdm_annotations.tsv').open(encoding='utf-8-sig',newline='') as f:tsv=list(csv.DictReader(f,delimiter='\t'))
    tsv_gold={}
    for row in tsv:
        paper=row['PaperName'];value=row['Result']
        try:value=json.loads(value)
        except (ValueError,TypeError):pass
        tsv_gold.setdefault(paper,{'TDMs':[]})['TDMs'].append({**{k:row[k] for k in FIELDS},'Result':value})
    tsv_summary,_=profile_annotations(tsv_gold);tsv_diff=annotation_diff(gold,tsv_gold)
    save(ROOT/'diagnostics/tsv_vs_json.json',{'source':str(gp.parent/'tdm_annotations.tsv'),'sha256':sha(gp.parent/'tdm_annotations.tsv'),'result_comparison_note':'For comparison only, numeric TSV Result tokens are JSON-decoded; all original text and source bytes preserved. TDM strings are never stripped or corrected.','summary':tsv_summary,'diff':tsv_diff})
    official_threshold2=[x for x in json_candidates if x.get('source_url') and x.get('readiness_threshold2_structure')]
    status='BLOCKED' if not official_threshold2 else 'REVIEW_REQUIRED'
    audit={'status':status,'frozen':frozen,'diagnostic_ge2':{'groups':len(diagnostic),'raw_records':sum(len(x['raw_rows']) for x in diagnostic),'different_papers':len({r['paper_id'] for x in diagnostic for r in x['raw_rows']}),'unique_tasks':len({x['tdm'][0] for x in diagnostic}),'scoring_allowed':False},'ge3_groups_missing_from_provided27':missing_ge3,'provided27_tdm_absent_from_annotations':[list(k) for k in bmap if k not in groups],'shared_board_differences':shared_diffs,'official_threshold2_candidates':official_threshold2,'candidate_boards':json_candidates,'annotation_versions':annotation_versions,'tsv_summary':tsv_summary,'tsv_vs_json_equal':tsv_diff['equal_structured_records'],'paper_reported_unique_tdm':138,'paper_reported_threshold2_boards':62,'unique_tdm_discrepancy_resolved':False,'new_llm_api_inference_calls':0,'formal_threshold2_evaluation_executed':False,'masking_preview_executed':False,'blocking_reasons':['No separately supplied official threshold2 leaderboard artifact found in local data or publicly downloaded ACL attachments.','62 reconstructed groups are diagnostic only and are explicitly not eligible for formal scoring.'] if not official_threshold2 else ['Candidate requires full provenance and shared-board compatibility review.']}
    save(ROOT/'data_audit.json',audit)
    save(ROOT/'source_manifest.json',{'retrieved_epoch':time.time(),'fetches':fetchlogs,'additional_access_failures':[{'source':'web tool official article + Tudatalib','failure':'network error decoding response body'},{'source':'Tudatalib via Windows Invoke-WebRequest with certificate checks','failure':'25-second operation timeout'},{'source':'Tudatalib via system curl with certificate checks','failure':'connection timeout after 10 seconds; HTTP 000'}],'archive_inventory':inventory,'json_sources':sources,'official_download_matches_local_original':{Path(a['path']).name:next((b['sha256']==a['sha256'] for b in inventory if b['source_url'] and b['source_url'].endswith(Path(a['path']).name)),False) for a in inventory if not a['source_url']},'local_readme':str(gp.parent/'README.md'),'readme_threshold_statement':'Minimum number of values for a leaderboard is 3; 27 leaderboards, 43 papers, 295 TDMRs.','archive_scripts_executed':False})
    print(json.dumps({'status':status,'frozen_gold':{k:gs[k] for k in ('papers','records','unique_tdm','groups_ge2','groups_ge3')},'provided_boards':{k:bs[k] for k in ('boards','records','different_papers','minimum_distinct_papers')},'diagnostic_ge2':audit['diagnostic_ge2'],'missing_ge3':len(missing_ge3),'provided27_tdm_absent':len(audit['provided27_tdm_absent_from_annotations']),'shared_differences':len(shared_diffs),'row_mismatches':len(bs['paper_tdm_result_mismatches']),'json_duplicate_keys':len(gdup)+len(bdup),'conflicting_paper_tdm':gs['conflicting_paper_tdm_count'],'tsv_records':tsv_summary['records'],'tsv_unique_tdm':tsv_summary['unique_tdm'],'tsv_vs_json_equal':tsv_diff['equal_structured_records']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
