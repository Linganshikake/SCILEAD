"""Transport fail-stop tests, no credential loading and no sockets."""
import types
from common import *
from engine import Transport
def main():
    setup();root=RUN/'reproducibility/failure_tests';assert not root.exists();root.mkdir()
    class Observe:
        stage='test';applied=0
        def expected(self,messages):return {'paper':'synthetic','record':1,'field':'Task','original':'A','messages':messages,'prompt_sha256':digest(messages),'candidate_serialized':"{'B'}",'candidate_sha256':digest("{'B'}")}
        def answer(self,*a):self.applied+=1
    outcomes={}
    for kind in ('timeout','truncation'):
        observer=Observe();t=Transport(root/kind,observer,mock=lambda _:None);sent=[0]
        def send():
            sent[0]+=1;a=t.active
            with (a['folder']/'attempt.json').open('x') as f:f.write('{}')
            if kind=='timeout':raise TimeoutError('Synthetic response unknown')
            body={'model':MODEL,'choices':[{'finish_reason':'length','message':{'role':'assistant','content':'partial'}}],'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}}
            a['state'].update(http_status=200,returned_model=MODEL,finish_reason='length',usage=body['usage']);save(a['folder']/'response.json',body);return None
        for repeat in range(2):
            try:t.generate([],send,lambda x:x)
            except (TimeoutError,AssertionError,RuntimeError):pass
            else:raise AssertionError('Failure must stop')
        assert sent[0]==1 and observer.applied==0 and t.cursor==0
        state=read(root/kind/'api_calls/0001/state.json');assert state['status']=='FAILED_OR_UNCERTAIN';outcomes[kind]={'send_count':sent[0],'state_applied':observer.applied,'automatic_retry_blocked':True}
    save(RUN/'reproducibility/failure_control_tests.json',{'status':'PASS','results':outcomes,'real_requests':0});print('FAILURE_CONTROLS_PASS',outcomes)
if __name__=='__main__':main()
