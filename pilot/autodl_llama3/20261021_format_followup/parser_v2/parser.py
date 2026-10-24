"""Frozen, deterministic structural recovery. No paper IDs or Gold dependencies."""
import json,math,hashlib
PREFIX='Here are the extracted tuples in JSON format:'
FIELDS={'Task','Dataset','Metric','Result'}
def pairs(items):
    result={}
    for k,v in items:
        if k in result:raise ValueError('DUPLICATE_KEY')
        result[k]=v
    return result
def bad(v):raise ValueError('NONFINITE')
D=json.JSONDecoder(object_pairs_hook=pairs,parse_constant=bad)
def schema(row):
    if not isinstance(row,dict) or set(row)!=FIELDS:return False
    if not all(isinstance(row[k],str) for k in ['Task','Dataset','Metric']):return False
    v=row['Result'];return not isinstance(v,bool) and isinstance(v,(str,int,float)) and (not isinstance(v,float) or math.isfinite(v))
def parse(text):
    groups=[];records=[];i=0;n=len(text);missing=False
    def ws(j):
        while j<n and text[j].isspace():j+=1
        return j
    def fail(reason,at):return {'ok':False,'text':None,'reason':reason,'offset':at,'groups':groups,'complete_record_spans':records}
    i=ws(i)
    if text.startswith(PREFIX,i):i=ws(i+len(PREFIX))
    try:
        while i<n:
            heading=None;fence=False
            if text.startswith('**',i):
                end=text.find('**',i+2)
                if end<0:return fail('UNFINISHED_HEADING',i)
                heading=text[i+2:end]
                if not heading or any(x in heading.lower().split() for x in ['corrected','revised','alternative','candidate','instead','revision']):return fail('AMBIGUOUS_HEADING',i)
                i=ws(end+2)
            if text.startswith('```json',i):i=ws(i+7);fence=True
            elif text.startswith('```',i):i=ws(i+3);fence=True
            if i>=n or text[i]!='[':return fail('UNAPPROVED_OUTER_TEXT',i)
            start=i;i=ws(i+1);local=[];rows=[];after_comma=False
            while True:
                if i==n:
                    if groups or not local or after_comma or fence:return fail('INCOMPLETE_ARRAY',i)
                    missing=True;end=i;break
                if text[i]==']':
                    if after_comma:return fail('TRAILING_COMMA',i)
                    end=i+1;i=ws(end);break
                if text[i]!='{':return fail('NOT_SELF_CONTAINED_OBJECT',i)
                row,j=D.raw_decode(text,i)
                if not schema(row):return fail('INVALID_FIELDS_OR_TYPES',i)
                item={'span':[i,j],'group_index':len(groups),'record_index':len(records),'result_type':type(row['Result']).__name__,'raw_sha256':hashlib.sha256(text[i:j].encode()).hexdigest()}
                local.append(item);records.append(item);rows.append(row);i=ws(j);after_comma=False
                if i<n and text[i]==',':i=ws(i+1);after_comma=True
                elif i<n and text[i]!=']':return fail('INVALID_RECORD_SEPARATOR',i)
            if heading is not None and (not rows or not any(all(row[k]==heading for row in rows) for k in ['Task','Dataset','Metric'])):return fail('HEADING_NOT_A_SELF_CONTAINED_GROUP_LABEL',start)
            if fence:
                if not text.startswith('```',i):return fail('UNPAIRED_FENCE',i)
                i=ws(i+3)
            groups.append({'span':[start,end],'heading':heading,'records':len(rows),'result_types':[type(row['Result']).__name__ for row in rows]})
        if not groups:return fail('NO_ARRAY',i)
        if len(groups)==1:
            a,b=groups[0]['span'];result=text[a:b]+(']' if missing else '')
            if not missing and not text[:a].strip() and not text[b:].strip():result=text
            rule='OUTER_CLOSE_ONLY' if missing else ('RAW_SINGLE_ARRAY' if result==text else 'V1_WRAPPER')
        else:
            result='['+','.join(text[x['span'][0]:x['span'][1]] for x in records)+']';rule='MERGE_COMPLETE_ARRAYS'
        values=D.decode(result);assert all(schema(x) for x in values) and len(values)==len(records)
        return {'ok':True,'text':result,'rule':rule,'groups':groups,'record_spans':records,'records':len(values),'outer_close_added':missing,'raw_sha256':hashlib.sha256(text.encode()).hexdigest(),'output_sha256':hashlib.sha256(result.encode()).hexdigest()}
    except (ValueError,TypeError) as e:return fail(str(e),i)
