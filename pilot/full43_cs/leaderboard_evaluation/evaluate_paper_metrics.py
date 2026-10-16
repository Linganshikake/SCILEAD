"""Supplementary paper-ID LR/AO; numeric conversion is delegated to official code."""
import collections,copy,importlib.metadata,inspect,math
from common import *
def ranking(values,metric):
    assert all(math.isfinite(v) for v in values.values()),'Nonfinite values need explicit analysis'
    lower=metric in ('Perplexity','TER')
    return [{'rank':i+1,'paper_id':p,'result':v} for i,(p,v) in enumerate(sorted(values.items(),key=lambda x:(x[1] if lower else -x[1],x[0])))]
def ao(gold_ids,pred_ids):
    k=min(len(gold_ids),len(pred_ids));details=[]
    for d in range(1,k+1):
        overlap=sorted(set(gold_ids[:d])&set(pred_ids[:d]));details.append({'depth':d,'gold_prefix':gold_ids[:d],'predicted_prefix':pred_ids[:d],'intersection':overlap,'agreement':len(overlap)/d})
    return (sum(x['agreement'] for x in details)/k if k else 0.0),details
def ties(values):
    grouped=collections.defaultdict(list)
    for p,v in values.items():grouped[v].append(p)
    return [{'result':v,'paper_ids':sorted(ps)} for v,ps in grouped.items() if len(ps)>1]
def main():
    boundary();verify_frozen()
    import leaderboard_eval as official
    import rbo
    gold_raw=read(GOLD);gold=read(RUN/'official/gold_after_official_conversion.json');pred=read(RUN/'official/generated_leaderboards.json');norm=read(NORMALIZED);raw=read(BASE/'merged/output.json');ev=read(RUN/'official/eval_values.json')['gold_results'];keys={str((g['Task'],g['Dataset'],g['Metric'])):g for g in gold}
    # Per-tuple conversion runs the unchanged original constructor on independent copies.
    # No extra cleaning, rounding, best-result selection, or replacement is performed.
    traces={k:[] for k in keys};outside=[];last_valid={k:{} for k in keys};tdm_hits=set()
    for paper,x in norm.items():
        raw_rows=json.loads(raw[paper]['output']);assert len(raw_rows)==len(x['normalized_output'])
        for index,t in enumerate(x['normalized_output'],1):
            key=str((t['Task'],t['Dataset'],t['Metric']))
            if key not in keys:
                outside.append({'paper':paper,'record':index,'tdmr':t,'reason':'TDM outside supplied 27 gold boards','null_fields':[k for k in ('Task','Dataset','Metric') if t[k] is None]});continue
            tdm_hits.add(key)
            single=official.construct_output_leaderboards(copy.deepcopy(gold_raw),{paper:{'normalized_output':[t]}})[key]
            converted=single.get(paper);finite=converted is not None and math.isfinite(converted)
            assert converted is None or finite,'Actual nonfinite conversion found; stop supplementary rankings'
            previous=last_valid[key].get(paper)
            trace={'paper':paper,'record':index,'raw_extraction':raw_rows[index-1],'normalized':t,'converted_result':converted,'valid_finite_result':finite,'replaces_previous_valid_record':previous['record'] if previous and finite else None,'selected_in_final_board':False}
            traces[key].append(trace)
            if finite:last_valid[key][paper]=trace
    for key in keys:
        assert {p:t['converted_result'] for p,t in last_valid[key].items()}==pred[key]
        for t in last_valid[key].values():t['selected_in_final_board']=True
    boards=[];by_tdm={};missing_details=[]
    for index,(original,g) in enumerate(zip(gold_raw,gold),1):
        key=str((g['Task'],g['Dataset'],g['Metric']));gv=g['Leaderboard'];pv=pred[key];gr=ranking(gv,g['Metric']);pr=ranking(pv,g['Metric']);gids=[x['paper_id'] for x in gr];pids=[x['paper_id'] for x in pr]
        score,depth=ao(gids,pids);assert abs(score-rbo.RankingSimilarity(gids,pids).rbo())<1e-12
        pc=ev['Paper Coverage'][key];rc=ev['Result Coverage'][key];rbo_score=ev['RBO'][key]
        assert pc==len(set(gv)&set(pv))/len(gv)
        numeric_hits=[{'predicted_paper':p,'predicted_result':v,'gold_papers_with_this_value':[gp for gp,gg in gv.items() if gg==v],'same_paper_result_correct':gv.get(p)==v} for p,v in pv.items() if v in gv.values()]
        assert rc==len(numeric_hits)/len(gv)
        joint=sum(p in gv and gv[p]==v for p,v in pv.items())/len(gv)
        missing=[]
        for paper in sorted(set(gv)-set(pv)):
            rs=json.loads(raw[paper]['output']);ns=norm[paper]['normalized_output'];compatible_null=[]
            for i,(a,b) in enumerate(zip(rs,ns),1):
                nulls=[k for k in ('Task','Dataset','Metric') if b[k] is None]
                if nulls and all(b[k] is None or b[k]==g[k] for k in ('Task','Dataset','Metric')):
                    compatible_null.append({'record':i,'raw':a,'normalized':b,'null_fields':nulls})
            missing.append({'paper':paper,'gold_result':gv[paper],'tdm_hits_in_predictions':[t for t in traces[key] if t['paper']==paper],'candidate_null_blocked_rows':compatible_null,'interpretation':'No accepted numeric prediction for this exact TDM. Null candidates match all remaining non-null labels; this is diagnostic evidence, not proof of a corrected mapping.'})
        board={'index':index,'Task':g['Task'],'Dataset':g['Dataset'],'Metric':g['Metric'],'tdm_key':key,'direction':'ascending' if g['Metric'] in ('Perplexity','TER') else 'descending','tie_policy':'numeric Result first, paper_id lexicographic ascending second; ordinal ranks','gold_original':original['Leaderboard'],'gold_official_numeric':gv,'predicted_official_numeric':pv,'gold_ranking':gr,'predicted_ranking':pr,'gold_ties':ties(gv),'prediction_ties':ties(pv),'Paper Coverage':pc,'Result Coverage':rc,'official_RBO_value_ranking':rbo_score,'AO_paper_id_ranking':score,'AO_depths':depth,'AO_k':min(len(gids),len(pids)),'empty':not pv,'tdm_hit_before_numeric_conversion':key in tdm_hits,'valid_result_nonempty':bool(pv),'extra_predicted_papers':sorted(set(pv)-set(gv)),'missing_gold_papers':sorted(set(gv)-set(pv)),'official_RC_numeric_hits':numeric_hits,'supplementary_joint_paper_result_coverage':joint,'numeric_conversion_trace':traces[key],'missing_paper_diagnostics':missing}
        assert all(math.isfinite(v) and 0<=v<=1 for v in (pc,rbo_score,score,joint));assert math.isfinite(rc) and rc>=0
        boards.append(board);by_tdm[key]={k:board[k] for k in ('index','Task','Dataset','Metric','direction','Paper Coverage','Result Coverage','official_RBO_value_ranking','AO_paper_id_ranking','AO_k','empty','tdm_hit_before_numeric_conversion','valid_result_nonempty','extra_predicted_papers','gold_ties','prediction_ties')}
        if not pv:missing_details.append({'tdm':key,'papers':missing})
    nonempty=sum(bool(x) for x in pred.values());aggregate={'gold_leaderboards':len(boards),'nonempty_valid_result_boards':nonempty,'tdm_hit_boards':len(tdm_hits),'LR_exact_tdm_hit':len(tdm_hits)/len(boards),'LR_nonempty_finite_result':nonempty/len(boards),'PC_official':sum(b['Paper Coverage'] for b in boards)/len(boards),'RC_official':sum(b['Result Coverage'] for b in boards)/len(boards),'RBO_official_value_rankings':sum(b['official_RBO_value_ranking'] for b in boards)/len(boards),'AO_paper_id_macro_all_gold_boards':sum(b['AO_paper_id_ranking'] for b in boards)/len(boards),'AO_nonempty_only_DIAGNOSTIC':sum(b['AO_paper_id_ranking'] for b in boards if not b['empty'])/nonempty if nonempty else 0,'supplementary_joint_paper_result_coverage':sum(b['supplementary_joint_paper_result_coverage'] for b in boards)/len(boards)}
    off=read(RUN/'official/eval_results.json')['gold_results'];assert all(abs(aggregate[a]-off[b])<1e-12 for a,b in [('PC_official','Paper Coverage'),('RC_official','Result Coverage'),('RBO_official_value_rankings','RBO')])
    settings={'LR_primary':'At least one exact normalized TDM match with finite numeric Result under original conversion. Exact-TDM-only alternative reported separately. No >=3 prediction filter is added.','AO':'(1/k) sum_{d=1..k} |G[:d] intersect M[:d]| / d, k=min(lengths); elements are paper IDs','AO_empty':'Zero when k=0; all 27 gold boards remain in macro denominator','AO_ties':'Sort Result using official metric direction, then paper_id ascending; no dense or fractional ranks','numeric_conversion':'Unmodified official constructor; duplicate (TDM,paper) uses last valid convertible tuple in original input order','RBO_library_version':importlib.metadata.version('rbo'),'RBO_signature':str(inspect.signature(rbo.RankingSimilarity.rbo)),'RBO_caveat':'Official rbo() default p=1 is unweighted overlap over deduplicated result-value rankings. Supplementary AO uses distinct paper IDs, retaining tied papers.','new_api_requests':0}
    save(RUN/'paper_metrics/leaderboard_metrics.json',{'aggregate':aggregate,'conventions':settings,'sources':{'paper_url':'https://aclanthology.org/2024.emnlp-main.453.pdf','formula_pdf_page':6,'table5_pdf_page':8,'gold_path':str(GOLD),'gold_sha256':sha(GOLD),'prediction_path':str(NORMALIZED),'prediction_sha256':sha(NORMALIZED)}})
    save(RUN/'paper_metrics/leaderboard_metrics_by_tdm.json',by_tdm);save(RUN/'leaderboards/gold_vs_predicted.json',boards);save(RUN/'paper_metrics/tuple_conversion_audit.json',{'matching_gold_tdm_rows':sum(len(x) for x in traces.values()),'outside_27_board_rows':outside,'unparseable_matching_rows':[t for ts in traces.values() for t in ts if not t['valid_finite_result']],'overwritten_matching_rows':[t for ts in traces.values() for t in ts if t['valid_finite_result'] and not t['selected_in_final_board']]});save(RUN/'paper_metrics/empty_board_diagnostics.json',missing_details)
    (RUN/'reference/installed_rbo_method.py.txt').write_text(inspect.getsource(rbo.RankingSimilarity.rbo),encoding='utf-8')
    verify_frozen();print(json.dumps(aggregate,ensure_ascii=False))
if __name__=='__main__':main()
