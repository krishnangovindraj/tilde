import re

class CC:
    GEN = 0
    WS = 1
    COMMA = 2
    STR = 3
    OPAR = 4
    CPAR = 5
    OLST = 6
    CLST = 7
    ESC = 8


    char_classes = {
        ' ': WS, '\n': WS, '\r': WS, '\t': WS,
        '(' : OPAR, ')' : CPAR,
        '[' : OLST, ']' : CLST,
        '\'' : STR, '\"' : STR, 
        ',' : COMMA,

        }


class PrologFactLikeParserError(Exception):
    def __init__(self, str):
        super(PrologFactLikeParserError, self).__init__(str)


class FlatPrologFactLikeParser:
    """ Assumes arguments are not functors or lists """
    
    fact_regex = r'([a-z][A-Za-z0-9_]*)\((.*)\).'
    fact_pattern = re.compile(fact_regex)
    

    def can_parse(self, line):
        return self.fact_pattern.match(line)
        
    def parse(self, line):
        match = self.can_parse(line)
        if match is not None:
            pred_name = match.group(1)
            arg_list = self.parse_arg_list(match.group(2))
        else:
            pred_name = None
            arg_list = None
        
        return pred_name, arg_list

    def parse_arg_list(self, arg_list_str):
        """ None if an error occurred """
            
        arg_list = []
        self.cursor = 0
        def tell_cursor():
            return self.cursor
        
        def next():
            self.cursor += 1

        def end_reached():
            return self.cursor >= len(arg_list_str)  
        
        def char_info():
            if end_reached():
                raise PrologFactLikeParserError("End reached while scanning")
            
            return arg_list_str[self.cursor], CC.char_classes.get(arg_list_str[self.cursor], 0)

        def skip_ws():
            while not end_reached():
                c, cc = char_info()
                if cc != CC.WS:
                    break
                next()

        def parse_escape_character():
            # Skip the next one
            next()
            next()

        def parse_string_literal():
            c, cc = char_info()
            end_char = c
            next()
            while not end_reached():
                c, cc = char_info()
                if cc == CC.ESC:
                    parse_escape_character()
                elif cc == CC.STR and end_char == c:
                    next()
                    return
                else:
                    next()

            raise PrologFactLikeParserError("Unterminated string literal")

        def parse_embedded_list():
            c, cc = char_info()
            end_cc = cc + 1 
            next()
            while not end_reached():
                c, cc = char_info()
                if cc == end_cc:
                    next()
                    break
                elif cc == CC.STR:
                    parse_string_literal()
                elif cc == CC.OLST:
                    parse_embedded_list()
                elif cc == CC.OPAR:
                    parse_embedded_list()
                else:
                    next()


        def parse_single_arg(end_char=None):
            skip_ws()
            arg_str = None
            start = tell_cursor()

            skip_ws()
            while not end_reached():
                c, cc = char_info()
                if cc == CC.WS or cc == CC.COMMA: 
                    break
                elif cc == CC.OLST or cc == CC.OPAR:
                    parse_embedded_list()
                elif cc == CC.STR:
                    parse_string_literal()
                elif cc == CC.ESC:
                    parse_escape_character()
                else:
                    next()
            # Or end reached
            arg_str = arg_list_str[start:tell_cursor()]
            skip_ws()
            return arg_str

        # Actual code of _parse
        while not end_reached():
            arg_str = parse_single_arg()
            arg_list.append(arg_str)

            if not end_reached():
                c, cc = char_info()
                if cc == CC.COMMA:
                    next()
                else:
                    raise PrologFactLikeParserError("Expected comma in arg#" + str(len(arg_list)) + " after: " + arg_str) 
    
        return arg_list


if __name__=='__main__':
    # Some tests ?
    def compare_output(pred_name, arg_list, expected_pred_name, expected_arg_list):

        return (pred_name == expected_pred_name and 
                len(arg_list) == len(expected_arg_list) and
                arg_list == expected_arg_list)

    def parse_test(s, expected_pred_name, expected_arg_list):
        failed = 0
        parser = PrologFactLikeParser()
        try:
            print("- " + s)
            pred_name, arg_list = parser.parse(s)
            
            print("\t- " + pred_name)
            for a in arg_list:
                print("\t* " + str(a))
            if compare_output(pred_name, arg_list, expected_pred_name, expected_arg_list):
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
    f += parse_test("simple_nospace(a,pq,xyz).", 'simple_nospace', ['a', 'pq', 'xyz'])
    f += parse_test("simple_lotsaspace( a, pq , xyz).", 'simple_lotsaspace', ['a', 'pq', 'xyz'])
    
    f += parse_test("numbers(1, 200, 11.23).", 'numbers', ['1', '200', '11.23'])

    f += parse_test("lists([a, b,c], pq, [d,e,f] ).", 'lists', ['[a, b,c]', 'pq', '[d,e,f]']) # We don't actually parse lists, so... 
    f += parse_test("functors(foo(a,b, c), bar(x, y ,z) ).", 'functors', ['foo(a,b, c)', 'bar(x, y ,z)'])
    
    f += parse_test("string(a, 'p,q,r,s', \"xyz\").", 'string', ['a', '\'p,q,r,s\'', '\"xyz\"'])
    f += parse_test("mixed_strings(a, 'p,q,\"r\",s', xyz).", 'mixed_strings', ['a', '\'p,q,\"r\",s\'', 'xyz'])
    
    f += parse_test("ecaped_string( a, 'p,q,\\\'foo\\\', s', xyz).", 'ecaped_string', ['a', '\'p,q,\\\'foo\\\', s\'', 'xyz'])

    if f > 0:
        print("TOTAL FAILURES = " + str(f))
    else:
        print("All tests succeeded!")