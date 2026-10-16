from common import *
def main():
    m=read(RUN/'manifest.json');counts={};failures=[]
    for stage,key in [('extract','extraction_dir'),('normalize','normalization_dir')]:
        completed=attempts=successes=records=0;active=[]
        for row in m['papers']:
            d=Path(row[key]);s=read(d/'summary.json') if (d/'summary.json').exists() else {}
            if s.get('status')=='COMPLETE':completed+=1;records+=s.get('records',0)
            elif s:failures.append({'paper':row['id'],'stage':stage,'summary':s})
            if (d/'api_usage.json').exists():
                u=read(d/'api_usage.json');attempts+=u['attempts'];successes+=u['successful_responses']
                if not s:active.append({'paper':row['id'],'recorded_attempts':u['attempts'],'successful_responses':u['successful_responses']})
        counts[stage]={'completed_papers':completed,'records':records,'attempts':attempts,'successful_responses':successes,'active':active}
    print(json.dumps({'stages':counts,'failures':failures},ensure_ascii=False))
if __name__=='__main__':main()
