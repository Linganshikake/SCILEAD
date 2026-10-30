"""Offline contract tests for the input ablation; never import API credentials."""
import unittest
import importlib.util
from pathlib import Path

class PreparationTests(unittest.TestCase):
    def test_preparation_adapter_is_available(self):
        self.assertTrue(Path(__file__).with_name('prepare_inputs.py').is_file(),
                        'The authorized input preparation adapter has not been implemented')

    def test_publication_artifacts_not_mixed_into_context(self):
        p=Path(__file__).with_name('prepare_inputs.py')
        self.assertTrue(p.is_file(), 'Missing preparation adapter')
        spec=importlib.util.spec_from_file_location('prep',p)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        docs=[{'content':'part one','metadata':{}},{'content':'Table 1: x 3','metadata':{}}]
        original=[{'role':'system','content':'unchanged instruction'},
                  {'role':'user','content':'Q\n\nRetrieved document contents:\n\npart one\n\nTable 1: x 3\n\n Output json:\n\n'}]
        text=m.replace_context(original,docs,[{'content':'full body','metadata':{}},docs[1]])
        self.assertEqual(text[0],original[0])
        self.assertEqual(text[1]['content'],'Q\n\nRetrieved document contents:\n\nfull body\n\nTable 1: x 3\n\n Output json:\n\n')
        images=m.image_messages(original,docs,['data:image/png;base64,AAA','data:image/png;base64,BBB'])
        self.assertEqual(images[0],original[0])
        self.assertEqual([p['image_url']['url'] for p in images[1]['content'] if p['type']=='image_url'],
                         ['data:image/png;base64,AAA','data:image/png;base64,BBB'])
        self.assertFalse(any('part one' in p.get('text','') for p in images[1]['content']))
        with self.assertRaises(ValueError):m.replace_context(original,[{'content':'wrong'}],docs)

if __name__=='__main__':unittest.main()
