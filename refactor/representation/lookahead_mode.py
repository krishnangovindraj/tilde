from typing import List

from problog.logic import Term, Var, And

# TODO: Caching
class LookaheadMode:
    PLACEHOLDER_VAR = Var('#')
    autoinc_var_idx = 0
    
    def __init__(self, pattern : List[Term], extension : List[Term]):
        pattern =  LookaheadMode.flatten_conjunction(pattern)
        
        self.sig = LookaheadMode.get_sig(pattern)
        self.pattern = pattern
        self.extension = extension
        # self.extension is set at the end.
        pattern_args = LookaheadMode.flatten_args(pattern)
        self.matching_args = [(i,j) for i in range(len(pattern_args)) for j in range(i+1, len(pattern_args)) if pattern_args[i]==pattern_args[j]]
                
        self.reused_args = {}
        self.reused_arg_indices = []
        
        extension_args = LookaheadMode.flatten_args([extension])
        for arg_index,t in enumerate(set(extension_args)):
            for i in range(len(pattern_args)):
                if pattern_args[i] == t:
                    self.reused_arg_indices.append(arg_index)
                    self.reused_args[t] = i
                    break
        
        # self.fresh_vars = set()
        # for t in extension_args:
        #     if t not in self.reused_args:
        #         self.fresh_vars.add(t)


    @staticmethod
    def flatten_args(conj: List[Term]):
        return [a for t in conj for a in t.args]

    @staticmethod
    def get_sig(conj : List[Term]):
        return tuple( (t.functor, t.arity) for t in conj )

    @staticmethod
    def flatten_conjunction(body):
        if body.functor == ',':
            bl = list(body.args)
            return  [bl[0]] + LookaheadMode.flatten_conjunction(bl[1])
        else:
            return [body]
    
    @staticmethod
    def list_to_conjunction(conj_list):
        def _ctl_rec(conj_list, at_index):
            if at_index == len(conj_list) - 2:
                return And(conj_list[at_index], conj_list[at_index+1])
            else:
                return And(conj_list[at_index], _ctl_rec(conj_list, at_index+1))
            
        if len(conj_list) > 1:
            return _ctl_rec(conj_list, 0)
        else:
            return conj_list[0]

    @staticmethod
    def from_declaration(lookahead_decl_str):
        lookahead_decl = Term.from_string(lookahead_decl_str)
        return LookaheadMode(lookahead_decl.args[0], lookahead_decl.args[1])

    def matches_pattern(self, candidate : List[Term]):
        if LookaheadMode.get_sig(candidate) == self.sig:
            flat_args = LookaheadMode.flatten_args(candidate)
            for test in self.matching_args:
                if flat_args[test[0]] != flat_args[test[1]]:
                    return False
            
            return True
        else:
            return False
    
    def get_extension_for_term(self, candidate: List[Term]):
        if not self.matches_pattern(candidate):
            raise ValueError("The candidate conjunction did not match the pattern")

        flattened_args = LookaheadMode.flatten_args(candidate)
        substitution = {k : flattened_args[self.reused_args[k]] for k in self.reused_args}
        for v in LookaheadMode.flatten_args([self.extension]):
            if v not in substitution:
                substitution[v] = LookaheadMode.PLACEHOLDER_VAR
        # for x in self.fresh_vars:
        #     LookaheadMode.autoinc_var_idx += 1
        #     substitution[x] = Var("LA_" + str(LookaheadMode.autoinc_var_idx))
            
        return self.extension.apply(substitution)
        