class DNFGenerator:
    """
        dnf_spec: List[List[int]]
        List[int] : [b1,b2,...,bk] where 1 <= |bi| <= n_variables and |bi| == |bj| <-> i == j
                    Each sublist represents a conjunction of variables. 
                        The x'th variable is in the conjunction iff x is in the sublist.
                        The negated x'th variable is in the conjunction iff -x is in the sublist
        
        List[ List[int] ]:
            The formula is a disjunction of each sublist
    """
    def __init__(self, n_variables, dnf_spec):
        self.n_variables = n_variables
        self.dnf_spec = dnf_spec 

    def check_conjunct(self, conj):
        for ds in self.dnf_spec:
            good = True
            for x in ds:
                idx = (x if x > 0 else -x)-1
                value = 1 if x > 0 else 0
                good = good and conj[idx] == value
            if good:
                return True
        return False


    def generate_all(self):
        good_conjuncts = []
        bad_conjuncts = []
        from itertools import product
        for p in product([0, 1], repeat = self.n_variables):
            if self.check_conjunct(p):
                good_conjuncts.append(p)
            else:
                bad_conjuncts.append(p)

        return good_conjuncts, bad_conjuncts

    @staticmethod
    def binary2intstr(bin, padding=0):
        i = 0
        for b in bin:
            i = i * 2 + b
        return str(i).zfill(padding)