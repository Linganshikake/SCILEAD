"""Original-main observer and same-position durable API response replay.

No normalization decisions replace official code: post-field assertions check
its actual locals. Trace hooks only persist state and compare replay events.
Transport is adapted from the previously validated scilead_api.py.
"""
import copy,inspect,logging,types
import common as c
from common import *

class Observer:
    def __init__(self,module,stage,out):
        self.module=module;self.stage=stage;self.out=Path(out);self.pending=None;self.event_index=0;self.call_index=0;self.events=[];self.initial=None
        source,start=inspect.getsourcelines(module.main)
        self.lines={s.strip():i+start for i,s in enumerate(source)}
        self.code=module.main.__code__
    def trace(self,frame,event,arg):
        if frame.f_code is not self.code:return None
        if event=='line':
            loc=frame.f_locals;line=frame.f_lineno
            if self.stage=='stage1':
                if line==self.lines['for key in tdm:'] and self.pending is not None:self.finish(loc)
                if line==self.lines["if key != 'Result' and tdm[key] not in labels_dict[key]:"]:
                    state=labels_state(loc['labels_dict'])
                    if self.initial is None:self.initial=state;immutable(self.out/'initial_labels.json',state)
                    self.pending={'paper':loc['paper'],'record':len(loc['normalized_tdms'])+1,'field':loc['key'],'original':loc['tdm'][loc['key']],'labels_before':state}
            else:
                if line==self.lines['normalized_tdm = tdm']:
                    self.pending={'paper':loc['paper'],'record':len(loc['normalized_tdms'])+1,'original':copy.deepcopy(loc['tdm']),'candidate_order':list(loc['leaderboard_tdm_set']),'candidate_serialized':'{'+', '.join(loc['leaderboard_tdm_set'])+'}'}
                    immutable(self.out/'candidates.json',{'ordered_values':list(loc['leaderboard_tdm_set']),'serialized':self.pending['candidate_serialized']})
                if line==self.lines['normalized_tdms.append(normalized_tdm)']:self.finish(loc)
        return self.trace
    def expected(self,messages):
        p=self.pending;assert p is not None
        if self.stage=='stage1':
            field=p['field'];serial=p['labels_before'][field]['serialized'];original=p['original']
        else:field='TDM';serial=p['candidate_serialized'];original='('+', '.join(p['original'][k] for k in ('Task','Dataset','Metric'))+')'
        prompts=read(PROMPT_PATH);key='masked-normalization-system-prompt' if self.stage=='stage1' else 'leaderboard-normalization-system-prompt'
        assert messages[0]=={'role':'system','content':prompts[key]} and len(messages)==2 and messages[1]['role']=='user'
        assert messages[1]['content']=='\n\nItem list: '+serial+'\n\nInput: '+original+'\n\nAnswer: '
        return {'run_id':RUN_ID,'paper':p['paper'],'record':p['record'],'field':field,'original':original,'candidate_serialized':serial,'candidate_sha256':digest(serial),'messages':messages,'prompt_sha256':digest(messages)}
    def answer(self,answer,index):self.pending['raw_answer']=answer;self.pending['call']=index;self.call_index=index
    def finish(self,loc):
        p=self.pending;assert p is not None;event=copy.deepcopy(p)
        if self.stage=='stage1':
            k=p['field'];old=p['original'];before=p['labels_before'];after=labels_state(loc['labels_dict']);actual=loc['normalized_tdm'][k];added=None
            if k=='Result' or old in before[k]['ordered_values']:expected=str(old);branch='exact_or_result';assert 'call' not in p
            else:
                a=p['raw_answer']
                if a in before[k]['ordered_values']:expected=a;branch='existing_candidate'
                elif a==old:expected=a;added=a;branch='original_name_added'
                else:expected=None;branch='null'
            assert actual==expected
            for key in before:assert set(after[key]['ordered_values'])==set(before[key]['ordered_values'])|({added} if added is not None and key==k else set())
            event.update(normalized=actual,branch=branch,added_name=added,labels_after=after)
        else:
            old=p['original'];expected=copy.deepcopy(old);branch='null_skipped' if any(old[k] is None for k in ('Task','Dataset','Metric')) else 'exact_tuple'
            if 'call' in p:
                if p['raw_answer'] in p['candidate_order']:
                    parts=p['raw_answer'][1:-1].split(', ')
                    for k,v in zip(('Task','Dataset','Metric'),parts[:3]):expected[k]=v
                    branch='tuple_mapped'
                else:branch='unmatched_preserved'
            assert loc['normalized_tdm']==expected;event.update(normalized=copy.deepcopy(loc['normalized_tdm']),branch=branch,changed=old!=expected)
        self.event_index+=1;event['event']=self.event_index;event['run_id']=RUN_ID
        immutable(self.out/'events'/f'{self.event_index:04d}.json',event)
        self.events.append(event)
        save(self.out/'checkpoint.json',{'status':'RUNNING','event':self.event_index,'paper':p['paper'],'record':p['record'],'field':p.get('field','TDM'),'last_call':self.call_index,'raw_answer':p.get('raw_answer'),'normalized':event['normalized'],'state_after':event.get('labels_after',{'candidate_order':p.get('candidate_order')}),'resume':'Replay saved responses from start, verify each prompt/state/event; no cross-position semantic cache'})
        self.pending=None

