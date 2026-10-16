from unittest.mock import patch
import common as c
def main():
    target=c.RUN/'reproducibility/atomic_write_test.json';original=c.Path.replace;calls=[]
    def temporarily_locked(self,destination):
        calls.append(str(destination))
        if len(calls)<=2:raise PermissionError('Synthetic Windows sharing conflict')
        return original(self,destination)
    with patch.object(c.Path,'replace',temporarily_locked):c.save(target,{'status':'PASS','value':'unchanged payload'})
    assert len(calls)==3 and c.read(target)=={'status':'PASS','value':'unchanged payload'}
    print('ATOMIC_WRITE_RETRY_PASS',len(calls))
if __name__=='__main__':main()
