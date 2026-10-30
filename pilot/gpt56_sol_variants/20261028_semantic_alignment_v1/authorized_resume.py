"""One explicitly approved unknown-transport recovery; frozen runtime unchanged."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CALL=ROOT/'cold_default/stage2/api_calls/0064'

def recover(folder,client,key,runtime):
 folder=Path(folder);authorization=runtime.read(folder/'manual_recovery_authorization.json')
 assert authorization['authorized'] is True and authorization['max_additional_attempts']==1
 assert authorization['request_sha256']==runtime.sha(folder/'request.json')
 assert authorization['original_state_sha256']==runtime.sha(folder/'state.json')
 state=runtime.read(folder/'state.json')
 assert state['status']=='UNKNOWN_TRANSPORT_ERROR' and state['error_type']=='RemoteProtocolError'
 assert not (folder/'response.json').exists() and not (folder/'accepted.json').exists()
 child=folder/'retry_1'
 assert not (child/'attempt.lock').exists(),'Authorized retry already attempted; inspect, never resend automatically'
 request=runtime.read(folder/'request.json')
 assert request==runtime.frozen.payload(request['messages']),'Frozen generation parameters differ'
 body=runtime.frozen.one_request(client,child,request,key,runtime.URL+'/chat/completions')
 answer=runtime.frozen.validate(body,False)
 runtime.save(folder/'accepted.json',{'status':'COMPLETE','response_relative_path':'retry_1/response.json',
   'response_sha256':runtime.sha(child/'response.json'),'raw_answer':answer,'finish_reason':'stop',
   'model':runtime.MODEL,'recovery':'ONE_USER_AUTHORIZED_UNKNOWN_TRANSPORT_RECOVERY'})
 return answer

def main():
 import variant_runtime as runtime
 runtime.setup();runtime.verify(full=True)
 assert runtime.read(ROOT/'recovery_offline_tests.json')['status']=='PASS'
 # Existing transport alone reads the designated credentials and creates its HTTP client.
 transport=runtime.Transport(None,ROOT/'cold_default/stage2',True)
 try:recover(CALL,transport.client,transport.key,runtime)
 finally:transport.client.close()
 runtime.save(ROOT/'cold_default/manual_resume_event.json',{'utc':runtime.frozen.now(),
   'call':str(CALL),'retry_accepted':True,'original_unknown_attempt_preserved':True,
   'action':'Resume cold_default stage2 using original positional replay'})
 return runtime.run_branch('cold_default')

if __name__=='__main__':sys.exit(main())
