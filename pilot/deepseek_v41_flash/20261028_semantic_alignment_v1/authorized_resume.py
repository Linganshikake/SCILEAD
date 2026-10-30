"""One explicitly authorized recovery for the specific unknown call; no auto retry."""
import sys,json
from pathlib import Path
from transport import load,save,digest,one_request,validate,load_credentials,BASE,now
ROOT=Path(__file__).resolve().parent
CALL=ROOT/'variants/cold_42/stage2/api_calls/0182'

def recover(folder,client,key):
 folder=Path(folder);authorization=load(folder/'manual_recovery_authorization.json')
 assert authorization['authorized'] is True and authorization['max_additional_attempts']==1
 assert authorization['request_sha256']==digest(folder/'request.json')
 assert authorization['original_state_sha256']==digest(folder/'state.json')
 state=load(folder/'state.json')
 assert state['status']=='UNKNOWN_TRANSPORT_ERROR' and state['error_type']=='RemoteProtocolError'
 assert not (folder/'response.json').exists() and not (folder/'accepted.json').exists()
 child=folder/'retry_1';assert not (child/'attempt.lock').exists(),'Additional attempt already exists; inspect, never resend automatically'
 body=one_request(client,child,load(folder/'request.json'),key,BASE+'/chat/completions')
 answer=validate(body,False)
 save(folder/'accepted.json',{'status':'COMPLETE','response_relative_path':'retry_1/response.json',
      'response_sha256':digest(child/'response.json'),'raw_answer':answer,'finish_reason':'stop',
      'model':'deepseek-flash','recovery':'ONE_USER_AUTHORIZED_UNKNOWN_TRANSPORT_RECOVERY'})
 return answer

def main():
 import httpx
 key,base=load_credentials();assert base==BASE
 with httpx.Client(transport=httpx.HTTPTransport(retries=0),trust_env=False,follow_redirects=False,
                   timeout=httpx.Timeout(connect=20,read=600,write=30,pool=20)) as client:
  recover(CALL,client,key)
 save(ROOT/'manual_resume_event.json',{'utc':now(),'call':str(CALL),'retry_accepted':True,
     'original_unknown_attempt_preserved':True,'action':'Resume cold_42 stage2 via original positional replay'})
 sys.path.insert(0,str(ROOT/'variants'))
 import variant_runtime as runtime
 return runtime.run_branch('cold_42')
if __name__=='__main__':sys.exit(main())
