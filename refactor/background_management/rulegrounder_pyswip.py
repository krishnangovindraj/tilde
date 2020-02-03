from pyswip import Prolog
from problog.logic import Term, Clause, Constant, Var

from .rulegrounder import RuleGrounder


"""
A primitive rule_grounder which just goes and queries the prolog program and collects all returned values.
"""
class PyswipRuleGrounder(RuleGrounder):
    """
    bg_program: pyswip.Prolog - Contains the rules. 
    kb_program: pyswip.Prolog - Contains the facts (about examples).
    """
    def __init__(self, bg_file, kb_file):
        self.prolog = Prolog()
        self.prolog.consult(bg_file)
        self.prolog.consult(kb_file)
    
    def update_kb(self, fact):
        self.prolog.asserta(fact)

    def find_models(self, sp_rule):
        # First verify that this is indeed a rule.
        groundings = []
        if isinstance(sp_rule, Clause): # hasattr(sp_rule, 'body'):
            # Just query the head
            head = sp_rule.head
            substitutions = list(self.prolog.query(head.repr))
            for sub in substitutions:
                grounded_args = {}
                for a in head.args:
                    if isinstance(a, Var):
                        var_str = str(a)
                        if var_str in sub:
                            grounded_args[var_str] = Constant( sub[var_str] ) # If it doesn't require a substitution, keep the variable
                        else:
                            grounded_args[var_str] = Var( var_str )
                groundings.append( head.apply(grounded_args) )
        
        return groundings



if __name__ == "__main__":
    # Hax test
    KB_FILE = '/mnt/e/courses/thesis/datasets/toy/even/even.kb'
    BG_FILE = '/mnt/e/courses/thesis/datasets/toy/even/even.bg'
    from problog.program import PrologFile
    pl = PrologFile(BG_FILE)
    rg = PyswipRuleGrounder(BG_FILE, KB_FILE)

    bg_rules = [ r for r in  pl if isinstance(r,Clause)]

    # Ok hacktime: I don't get this.
    e4 = bg_rules[1].apply( {'X': Constant(4), 'Y': Var('Y') } )
    groundings = rg.generate_groundings(e4)
    print(groundings)