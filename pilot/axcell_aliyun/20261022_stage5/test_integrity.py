import unittest,tempfile,json,hashlib
from pathlib import Path
import run_normalization as runner
class IntegrityTests(unittest.TestCase):
    def test_changed_copy_rejected_without_generation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/'paper';source=folder/'normalization/normalized_output.json';source.parent.mkdir(parents=True)
            data={'paper':{'normalized_output':[{'Task':'correct','Result':'1'}]}}
            source.write_text(json.dumps(data));copy=root/'copy.json';copy.write_text(json.dumps({'paper':{'normalized_output':[{'Task':'changed','Result':'1'}]}}))
            state={'normalized_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            with self.assertRaises(AssertionError):runner.verified_output(folder,copy,state)
    def test_equivalent_copy_returns_verified_original(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);folder=root/'paper';source=folder/'normalization/normalized_output.json';source.parent.mkdir(parents=True)
            data={'paper':{'normalized_output':[]}};source.write_text(json.dumps(data,indent=4));copy=root/'copy.json';copy.write_text(json.dumps(data,indent=2))
            state={'normalized_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            self.assertEqual(runner.verified_output(folder,copy,state),data)
if __name__=='__main__':unittest.main()
