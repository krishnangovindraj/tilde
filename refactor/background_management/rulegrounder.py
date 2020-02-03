from pyswip import Prolog
from problog.logic import Term, Clause, Constant, Var


class RuleGrounder:
    """ 
    Updates the knowledge base with the given fact
    """ 
    def update_kb(self, fact):
        pass

    """
    sp_rule must have all +arguments already grounded.
    returns a dict:VarName:str -> Substitution:Term
    """
    def find_models(self, rule):
        raise NotImplementedError("Abstract method")

    