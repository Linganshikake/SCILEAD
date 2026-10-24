import unittest, tempfile, pathlib, hashlib
from policy import checkpoint_action, resource_stop, owned_unit, recovered_stop, owns_service

class Guards(unittest.TestCase):
 def test_no_retry_uncertain_or_failed(self):
  for state in ['RUNNING','FAILED','BLOCKED']:
   self.assertEqual(checkpoint_action({'status':state},True), 'BLOCK')
 def test_first_and_verified_skip(self):
  self.assertEqual(checkpoint_action(None,False),'START')
  for state in ['EXTRACTION_COMPLETE','VALID_EMPTY']:
   self.assertEqual(checkpoint_action({'status':state},True),'SKIP')
   self.assertEqual(checkpoint_action({'status':state},False),'BLOCK')
 def test_orphan_output_blocks(self):
  self.assertEqual(checkpoint_action(None,True),'BLOCK')
 def test_early_resource_stops(self):
  base=dict(available=28*2**30,free=50*2**30,worker=5*2**30,es=1.5*2**30,oom=1,baseline_oom=1,elapsed=10)
  self.assertIsNone(resource_stop(**base))
  for key,value in [('available',3*2**30),('free',19*2**30),('worker',14*2**30),('es',2.5*2**30),('oom',2),('elapsed',3601)]:
   self.assertIsNotNone(resource_stop(**dict(base,**{key:value})),key)
 def test_owned_cleanup_only(self):
  self.assertTrue(owned_unit('axcell-stage3-worker-01.service'))
  for x in ['ssh.service','axcell-single-es','axcell-stage3-worker-../ssh.service','axcell-stage3-worker-.service']:
   self.assertFalse(owned_unit(x))
 def test_durable_resource_failure_blocks_resume(self):
  self.assertEqual(recovered_stop([{'status':'FAILED','resource_stop':'NEW_KERNEL_OOM'}]),'NEW_KERNEL_OOM')
  self.assertIsNone(recovered_stop([{'status':'FAILED','error':'paper error'}]))
 def test_exact_service_ownership(self):
  self.assertTrue(owns_service({'Description':'scilead-stage3-abc'},'abc'))
  self.assertFalse(owns_service({'Description':'old-task'},'abc'))

if __name__=='__main__':unittest.main()
