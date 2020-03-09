import re
from .flat_prolog_fact_like_parser import FlatPrologFactLikeParser
class TERM_TYPE:
    CONSTANT = 1
    FUNCTOR = 2
    LIST = 3
    STRING = 4

    REVERSE_MAP = {1: "const", 2: "func", 3: "list", 4: "str"}

class PrologLikeTerm:

    def __init__(self, term_type, term_name, value_list = None):
        self.name = term_name
        self.term_type = term_type
        self.value_list = value_list

    def __eq__(self, other):
        return (
            self.term_type == other.term_type and 
            self.name == other.name and
            self.value_list == other.value_list
        )

    def __str__(self):
        if self.value_list is not None:
            return ( TERM_TYPE.REVERSE_MAP[self.term_type] + ":" + str(self.name) + "(" + ", ".join([str(t) for t in self.value_list ]) + ")" )
        else:
            return ( TERM_TYPE.REVERSE_MAP[self.term_type] + ":" + str(self.name) ) 

class RecursivePrologFactLikeParser:
    
    const_regex = r'^([a-z][A-Za-z0-9_]*)$'
    const_pattern = re.compile(const_regex)

    pred_regex = r'^([a-z][A-Za-z0-9_]*)\((.*)\)$'
    pred_pattern = re.compile(pred_regex)
    
    list_regex = r'^\[(.*)\]$'
    list_pattern = re.compile(list_regex)

    single_quote_string_regex = r'^\'(.*)\'$'
    single_quote_string_pattern = re.compile(single_quote_string_regex)

    double_quote_string_regex = r'\"(.*)\"'
    double_quote_string_pattern = re.compile(double_quote_string_regex)

    def parse(self, fact_str):
        self.parser = FlatPrologFactLikeParser()
        match = self.parser.can_parse(fact_str)
        if match is not None:
            # Group 0 has the whole match
            return self._parse(match.group(0).rstrip('.'))
        else:
            return None

    def _parse_arg_list(self, arg_list_str):
        untyped_args = self.parser.parse_arg_list(arg_list_str)
        if untyped_args is not None:
            # We good.
            return [ self._parse(a) for a in untyped_args ]
        else:
            return None

    def _parse(self, term_str):

        match = self.const_pattern.match(term_str)
        if match is not None:
            return PrologLikeTerm(TERM_TYPE.CONSTANT, match.group(1))
        
        match = self.pred_pattern.match(term_str)
        if match is not None:
            pred_name = match.group(1)
            arg_list = self._parse_arg_list(match.group(2))
            if pred_name is not None and arg_list is not None:
                # We good.
                return PrologLikeTerm(TERM_TYPE.FUNCTOR, pred_name, arg_list)
            else:
                return None

        match = self.list_pattern.match(term_str)
        if match is not None:
            arg_list = self._parse_arg_list(match.group(1))
            if arg_list is not None:
                return PrologLikeTerm(TERM_TYPE.LIST, None, arg_list)


        # Need to try single and double quotes
        match = self.single_quote_string_pattern.match(term_str)
        if match is None:
            match = self.double_quote_string_pattern.match(term_str)

        if match is not None:
            return PrologLikeTerm(TERM_TYPE.STRING, match.group(1))

        # If by this point nothing matches, return None
        return None




if __name__=='__main__':
    # Some tests ?
    def parse_test(s, expected_term):
        failed = 0
        parser = RecursivePrologFactLikeParser()
        try:
            print("- " + s)
            term = parser.parse(s)
            
            print(term)
            if term is not None and term == expected_term:
                print("success")
            else:
                failed = 1
                print("FAILURE")
            
        except Exception as e:
            print("Exception: " + str(e))
            raise e
        print()
        return failed


    f = 0
    PLT = PrologLikeTerm
    f += parse_test("simple_nospace(a, pq).", PLT(TERM_TYPE.FUNCTOR, "simple_nospace", [PLT(TERM_TYPE.CONSTANT, 'a'), PLT(TERM_TYPE.CONSTANT, 'pq')]))
    # f += parse_test("simple_lotsaspace( a, pq , xyz).", 'simple_lotsaspace', ['a', 'pq', 'xyz'])
    
    # f += parse_test("numbers(1, 200, 11.23).", 'numbers', ['1', '200', '11.23'])

    f += parse_test("lists([a, b,c], pq, [d,e,f] ).", PLT(TERM_TYPE.FUNCTOR, 'lists', [
            PLT(TERM_TYPE.LIST, None, [PLT(TERM_TYPE.CONSTANT, 'a'), PLT(TERM_TYPE.CONSTANT, 'b'), PLT(TERM_TYPE.CONSTANT, 'c')]),
            PLT(TERM_TYPE.CONSTANT, 'pq'), 
            PLT(TERM_TYPE.LIST, None, [PLT(TERM_TYPE.CONSTANT, 'd'), PLT(TERM_TYPE.CONSTANT, 'e'), PLT(TERM_TYPE.CONSTANT, 'f')])
            ]
            )
        )
    
    f += parse_test("functors(foo(a,b, c), bar(x, y ,z) ).", 
        PLT(TERM_TYPE.FUNCTOR, 'functors', [
            PLT(TERM_TYPE.FUNCTOR, 'foo', [PLT(TERM_TYPE.CONSTANT, 'a'), PLT(TERM_TYPE.CONSTANT, 'b'),PLT(TERM_TYPE.CONSTANT, 'c')]),
            PLT(TERM_TYPE.FUNCTOR, 'bar', [PLT(TERM_TYPE.CONSTANT, 'x'), PLT(TERM_TYPE.CONSTANT, 'y'),PLT(TERM_TYPE.CONSTANT, 'z')]),
            ])
        )
    
    f += parse_test("string(a, 'p,q,r,s', xyz).", 
        PLT(TERM_TYPE.FUNCTOR, 'string', [
            PLT(TERM_TYPE.CONSTANT, 'a'), PLT(TERM_TYPE.STRING, 'p,q,r,s'), PLT(TERM_TYPE.CONSTANT, 'xyz')
            ])
        ) 
    
    if f > 0:
        print("TOTAL FAILURES = " + str(f))
    else:
        print("All tests succeeded!")