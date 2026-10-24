"""Offline candidate only. Never invoked by generation or normalization.

Keep the unique complete JSON array verbatim. Do not edit fields, numbers or records.
Formal use requires the user's explicit approval of this particular protocol.
"""
import json,math,hashlib
FIELDS={'Task','Dataset','Metric','Result'}
PREFIXES={'','Here are the extracted tuples in JSON format:'}
def pairs(values):
    d={}
    for k,v in values:
        if k in d:raise ValueError('duplicate key')
        d[k]=v
    return d
def bad_constant(v):raise ValueError('nonfinite constant')
DECODER=json.JSONDecoder(object_pairs_hook=pairs,parse_constant=bad_constant)
def schema(rows):
    if not isinstance(rows,list):return False
    for x in rows:
        if not isinstance(x,dict) or set(x)!=FIELDS:return False
        if not all(isinstance(x[k],str) for k in ['Task','Dataset','Metric']):return False
        r=x['Result']
        if isinstance(r,bool) or not isinstance(r,(str,int,float)):return False
        if isinstance(r,float) and not math.isfinite(r):return False
    return True
def audit(text):
    r={'raw_json_valid':False,'raw_schema_acceptable':False,'unique_complete_array':False,'candidate_eligible':False,'candidate_applied_to_formal':False,'candidate_text':None,'records':None,'result_types':[],'record_values_unchanged':False,'official_schema_acceptable':False}
    try:
        raw=DECODER.decode(text);r['raw_json_valid']=True;r['raw_schema_acceptable']=schema(raw)
    except ValueError:raw=None
    # Decode each structural start, then retain outermost spans. Nested row objects
    # are not additional outputs. Reject structural residue outside the candidate.
    spans=[]
    for start,ch in enumerate(text):
        if ch not in '[{':continue
        try:value,end=DECODER.raw_decode(text,start)
        except ValueError:continue
        if isinstance(value,(dict,list)):spans.append((start,end,value))
    outer=[x for x in spans if not any(y[0]<x[0] and x[1]<=y[1] for y in spans)]
    r['outer_structures']=len(outer)
    if len(outer)!=1:r['reason']='NON_UNIQUE_OR_INCOMPLETE_STRUCTURE';return r
    start,end,rows=outer[0];before=text[:start];after=text[end:]
    if not isinstance(rows,list) or any(c in before+after for c in '[]{}'):
        r['reason']='NOT_ONE_COMPLETE_TOP_LEVEL_ARRAY';return r
    r.update(unique_complete_array=True,records=len(rows),result_types=[type(x.get('Result')).__name__ if isinstance(x,dict) else type(x).__name__ for x in rows],prefix=before,suffix=after,span=[start,end],official_schema_acceptable=schema(rows))
    p=before.strip();s=after.strip()
    if p.endswith('```json'):p=p[:-7].strip();fence=True
    elif p.endswith('```'):p=p[:-3].strip();fence=True
    else:fence=False
    if p not in PREFIXES or (s!='```' if fence else s!=''):
        r['reason']='UNAPPROVED_PREFIX_OR_SUFFIX';return r
    if not schema(rows):r['reason']='INVALID_FIELDS_OR_VALUE_TYPES';return r
    candidate=text[start:end]
    assert DECODER.decode(candidate)==rows
    r.update(candidate_eligible=True,candidate_text=candidate,record_values_unchanged=True,candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),reason='RAW_ALREADY_VALID' if r['raw_json_valid'] else 'CANDIDATE_ONLY_REQUIRES_USER_APPROVAL')
    return r
