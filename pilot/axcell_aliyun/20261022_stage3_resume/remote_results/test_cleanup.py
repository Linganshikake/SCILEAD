import sys,unittest,tempfile
from pathlib import Path
from unittest.mock import patch,MagicMock
if sys.platform=='win32':sys.modules['fcntl']=MagicMock()
import controller as c
class Cleanup(unittest.TestCase):
 def test_timeout_each_resource_still_killed(self):
  state={'unit':True,'es':True};calls=[]
  def info(unit):return {'Description':'scilead-stage3-token','ActiveState':'active' if state['unit'] else 'inactive','LoadState':'loaded'}
  def docker(name):return {'Id':'owned-id','Config':{'Labels':{'scilead.task':c.LABEL,'scilead.attempt':'token'}},'State':{'Running':state['es']}}
  def cmd(args,*a,**kw):
   calls.append(args)
   if args[:2]==['systemctl','kill']:state['unit']=False
   if args[:2]==['docker','kill']:state['es']=False
   return {'code':0,'stdout':'','stderr':''}
  with tempfile.TemporaryDirectory() as td,patch.object(c,'unitinfo',info),patch.object(c,'container',docker),patch.object(c,'cmd',cmd),patch.object(c,'vmstat',lambda:{'oom_kill':1}),patch.object(c,'cleanup_command',side_effect=TimeoutError('simulated')):
   r=c.stop_owned('axcell-stage3-worker-token.service','own-es',Path(td),1,'token')
  self.assertTrue(r['clean']);self.assertEqual(len(r['errors']),2)
  self.assertTrue(any(x[:2]==['systemctl','kill'] for x in calls));self.assertTrue(any(x[:2]==['docker','kill'] for x in calls))
 def test_unowned_unit_not_stopped(self):
  with tempfile.TemporaryDirectory() as td,patch.object(c,'unitinfo',lambda u:{'Description':'other-task','LoadState':'loaded','ActiveState':'active'}),patch.object(c,'container',lambda n:None),patch.object(c,'vmstat',lambda:{'oom_kill':1}),patch.object(c,'cleanup_command') as stop:
   r=c.stop_owned('axcell-stage3-worker-token.service','own-es',Path(td),1,'token')
  stop.assert_not_called();self.assertFalse(r['clean']);self.assertIn('UNOWNED_UNIT_NOT_STOPPED',r['errors'])
if __name__=='__main__':unittest.main()
