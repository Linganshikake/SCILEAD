"""Safety tests: low disk/memory and resume integrity, with no Docker/model use."""
import tempfile, unittest
from pathlib import Path
import policy

class Guards(unittest.TestCase):
    def test_start_disk_and_ram(self):
        self.assertEqual(policy.start_guard(6*2**30,20*2**30),None)
        self.assertEqual(policy.start_guard(6*2**30,20*2**30-1),'DISK_RESERVE')
        self.assertEqual(policy.start_guard(6*2**30-1,30*2**30),'START_LOW_MEMORY')
    def test_disk_runtime(self):
        self.assertEqual(policy.disk_guard(20*2**30-1),'DISK_RESERVE')
        self.assertIsNone(policy.disk_guard(20*2**30))
    def test_resume_rejects_mutated_output_and_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'text.json';p.write_text('original')
            d={'input_sha256':'A','configuration_sha256':'B','artifacts':[{'path':str(p),'sha256':policy.sha(p),'bytes':p.stat().st_size}]}
            self.assertTrue(policy.reusable(d,'A','B'))
            self.assertFalse(policy.reusable(d,'C','B'))
            self.assertFalse(policy.reusable(d,'A','C'))
            p.write_text('changed')
            self.assertFalse(policy.reusable(d,'A','B'))
    def test_partial_is_not_success(self):
        self.assertFalse(policy.reusable({'input_sha256':'A','configuration_sha256':'B','artifacts':[]},'A','B'))

if __name__=='__main__':unittest.main()
