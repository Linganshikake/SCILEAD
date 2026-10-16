"""Independent hand-calculated formula and edge-case checks; never invokes a model."""
import math
from common import *
from evaluate_paper_metrics import ao,ranking
def main():
    boundary();cases=[(['a','b','c'],['a','b','c'],1),(['a','b','c'],['c','b','a'],.5),(['a','b','c'],['a'],1),(['a','b'],['x','y'],0),(['a'],[],0),([],[],0),(['a','b','c'],['b','a'],.5)]
    for g,p,v in cases:assert math.isclose(ao(g,p)[0],v,abs_tol=1e-12),(g,p)
    assert [x['paper_id'] for x in ranking({'z':10,'a':10,'b':11},'Accuracy')]==['b','a','z']
    assert [x['paper_id'] for x in ranking({'z':10,'a':10,'b':11},'Perplexity')]==['a','z','b']
    assert [x['paper_id'] for x in ranking({'a':.2,'b':.1},'TER')]==['b','a']
    import leaderboard_eval as official
    g=[{'Task':'t','Dataset':'d','Metric':'Accuracy','Leaderboard':{'gold':.9}}];k=str(('t','d','Accuracy'))
    o=official.construct_output_leaderboards(g,{});assert len(o)==1 and not o[k] and g[0]['Leaderboard']['gold']==90
    def entry(value):return {'Task':'t','Dataset':'d','Metric':'Accuracy','Result':value}
    o=official.construct_output_leaderboards(g,{'p':{'normalized_output':[entry('0.81 ± 0.02'),entry('82%'),entry('not numeric')]}});assert o[k]['p']==82
    o=official.construct_output_leaderboards(g,{'p':{'normalized_output':[entry('1')]}});assert o[k]['p']==1
    scores=official.evaluate({k:{'wrong-paper':90}},g);assert scores['Paper Coverage'][k]==0 and scores['Result Coverage'][k]==1
    save(RUN/'paper_metrics/formula_tests.json',{'status':'PASS','hand_calculated_AO_cases':len(cases),'ranking_direction_and_tie_cases':3,'official_rule_checks':['precreated_empty_keys_not_LR_hits','gold_scaling','plus_minus_and_percent_cleaning','last_valid_write_wins','invalid_does_not_erase_previous','one_not_scaled','RC_does_not_require_paper_match'],'new_api_requests':0})
    print('Formula, tie/empty handling and official conversion checks PASS')
if __name__=='__main__':main()
