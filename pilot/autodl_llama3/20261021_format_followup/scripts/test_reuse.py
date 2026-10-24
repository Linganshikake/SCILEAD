import unittest,copy
from reuse_contract import reusable
class ReuseTests(unittest.TestCase):
    def setUp(self):self.a={'context':{'paper_id':'P','record_index':1,'field':'Dataset','source_row':{'Dataset':'X','Result':1},'candidate_state':{'Task':['T'],'Dataset':['D']},'candidate_serialization':"{'D'}",'partial_row':{}},'request':{'prompt':'exact','seed':0,'max_new_tokens':15,'model_revision':'fixed'}}
    def test_exact(self):self.assertTrue(reusable(self.a,copy.deepcopy(self.a)))
    def test_position_not_name_cache(self):
        b=copy.deepcopy(self.a);b['context']['record_index']=2;self.assertFalse(reusable(self.a,b))
    def test_changed_state_even_same_prompt(self):
        b=copy.deepcopy(self.a);b['context']['candidate_state']['Task'].append('new');self.assertFalse(reusable(self.a,b))
    def test_changed_request(self):
        for k,v in [('prompt','different'),('seed',1),('max_new_tokens',16),('model_revision','other')]:
            b=copy.deepcopy(self.a);b['request'][k]=v;self.assertFalse(reusable(self.a,b))
    def test_changed_source_row(self):
        b=copy.deepcopy(self.a);b['context']['source_row']['Result']=2;self.assertFalse(reusable(self.a,b))
    def test_order_change(self):
        b=copy.deepcopy(self.a);b['context']['candidate_serialization']="{'E', 'D'}";self.assertFalse(reusable(self.a,b))
if __name__=='__main__':unittest.main(verbosity=2)
