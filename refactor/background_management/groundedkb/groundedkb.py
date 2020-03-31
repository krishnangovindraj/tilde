from problog.logic import Term, Var, Constant
from problog.program import LogicProgram
from pyswip import Prolog

""" Abstract class/interface  """
class GroundedKB:

    def setup(self):
        raise NotImplementedError("Abstract method")

    def add_fact(self, fact):
        raise NotImplementedError("Abstract method")

    def query_fact(self, fact):
        raise NotImplementedError("Abstract method")
    
    def add_many_facts(self, facts):
        raise NotImplementedError("Abstract method")

    """ Derives groundings of `rule` entailed by the KB """
    def derive_groundings(self, rule):
        raise NotImplementedError("Abstract method")

    """ Derives those groundings of `rule` entailed by (KB AND new_ground_fact) but not by KB alone """
    def derive_groundings_incremental(self, rule, new_ground_fact):
        raise NotImplementedError("Abstract method")

    def saturate_examples(self, examples):
        raise NotImplementedError("Abstract method")
