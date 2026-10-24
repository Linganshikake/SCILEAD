"""Regression checks for review findings; no containers or paper/model generation."""
import unittest
import policy
class ResumeAndCleanup(unittest.TestCase):
    def test_cleanup_failure_overrides_timeout(self):
        self.assertEqual(policy.final_stop_reason('OWNED_STAGE_TIMEOUT',{'process_group':{'remaining_live_members':[{'pid':1}]}}),'TASK_CLEANUP_INCOMPLETE')
        self.assertEqual(policy.final_stop_reason('OWNED_STAGE_TIMEOUT',{'containers':{'remaining_running_task_containers':['abc']}}),'TASK_CLEANUP_INCOMPLETE')
        self.assertEqual(policy.final_stop_reason('OWNED_STAGE_TIMEOUT',{'process_group':{'remaining_live_members':[]}}),'OWNED_STAGE_TIMEOUT')
    def test_unattempted_resource_block_can_resume(self):
        self.assertEqual(policy.resume_state('BLOCKED',False,False),'PENDING')
        self.assertEqual(policy.resume_state('BLOCKED',True,False),'BLOCKED')
        self.assertEqual(policy.resume_state('FAILED',True,True),'FAILED')
    def test_completed_child_recovered_without_regeneration(self):
        self.assertEqual(policy.resume_state('RUNNING',True,True),'PARSE_COMPLETE')
        self.assertEqual(policy.resume_state('RUNNING',True,False),'BLOCKED')
if __name__=='__main__':unittest.main()
