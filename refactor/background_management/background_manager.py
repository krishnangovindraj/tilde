"""
Assumptions made:
* All information related to the examples are in .kb file
* No Information not related to any example is in the .kb file
* All (background) knowledge (which could apply to any example) are in the bg file
"""

from refactor.representation.language import TypeModeLanguage
from .rulegrounder_pyswip import PyswipRuleGrounder
from refactor.tilde_essentials.example import Example
from problog.logic import Term, Var, Constant
from problog.program import LogicProgram

# class RModeDescriptor:
#     def __init__(self, functor, arity, arg_mode_types):
#         self.functor = functor
#         self.arity = arity
#         self.in_args  = [ a[1] for a in arg_mode_types if a[0] == '+']
#         self.out_args = [ a[1] for a in arg_mode_types if a[0] == '-']



# def argument_combinations(functor, signature, type_val_map, new_var_index, new_var_val):
def argument_combinations(functor, signature,  const_val_map, type_val_map,new_var):
    # RECURSIVE GENERATORS YAY!
    
    def _argument_combination_generator(ac, const_val_map, type_val_map, signature, new_var_index, new_var_val, at_index):
        if at_index < 0:
            yield #[]
        else:
            # for ac 
            for _ in _argument_combination_generator(ac, const_val_map, type_val_map, signature, new_var_index, new_var_val, at_index-1):     
                if  at_index == new_var_index:
                    ac[at_index] = new_var_val #ac.append(new_var_val)
                    yield # ac
                elif signature[at_index][0] == '+':
                    # ac.append('_')
                    for v in type_val_map[ signature[at_index][1] ]:
                        ac[at_index] = v
                        yield # ac
                elif signature[at_index][0] == 'c':
                    const_arg_key = functor+'_'+str(at_index)
                    for v in const_val_map[const_arg_key]:
                        ac[at_index] = v
                        yield
                elif signature[at_index][0] == '-':
                    # Append a variable and return
                    ac[at_index] = Var('V_' + str(at_index)) # ac.append('V_' + str(at_index))
                    yield # ac


    # Add a_n in
    multidict_safe_add(type_val_map, new_var[0], new_var[1])
    for new_var_index in [i for i in range(len(signature)) if signature[i] == ('+', new_var[0])]:
        # print("new_var_index=" + str(new_var_index))
        ac = ["_"] * len(signature)
        # Sorry python :(
        for _ in _argument_combination_generator(ac, const_val_map, type_val_map, signature, new_var_index, new_var[1], len(signature)-1):
            yield Term(functor, *ac)


def multidict_safe_add(d, k, v):
    if k not in d:
        d[k] = set()
    d[k].add(v)

def multidict_safe_multiadd(d, kv_list):
    for (k,v) in kv_list:
        multidict_safe_add(d, k, v)

def term2pyswip(term):
    return "%s(%s)"%(term.functor, ','.join(map(str, term.args)))


class BackgroundManager:
    
    def __init__(self, prediction_goal, language, bg_program_file): # 

        self._bg_program_file = bg_program_file
        self.prediction_goal = prediction_goal
        self.language = language
        # self.bg_program = None
        self.db = {}

        self.funcsig = {}       # functor:str -> list( tuple(arg_mode:str, arg_type:str))
        self.const_vals = {}    # tuple(functor:str, arg_index:int) -> set(val:str)
        self.intype2func = {}   # arg_type:str -> list(functor:str)
        self.out_args = {}      # functor:str -> list(arg_index:int)

        self.rules = {}         # functor:str -> rule:?
        self.groundings = {}    # functor: str -> list(term:?)
    
    def setup(self):
        self._process_language(self.prediction_goal, self.language)
        self._process_bg_program(self._bg_program_file)

    def has_groundings(self, functor, arity):
        return (functor,arity) in self.db
    
    def get_groundings(self, functor, arity):
        return self.db.get( (functor,arity), None)

    def add_groundings(self, functor, arity, groundings):
        if (functor,arity) in self.db:
            self.db[(functor, arity)] += groundings
        else:
            self.db[(functor, arity)] += groundings


    def _process_language(self, prediction_goal, language:TypeModeLanguage):
        # Add the prediction goal
        self.funcsig[prediction_goal.functor] = [('-', arg_type) for arg_type in language.get_argument_types(prediction_goal.functor, prediction_goal.arity) ]
        
        # TODO: Modes are not one-to-one
        for rmode in language.get_refinement_modes():
            functor = rmode[0]
            type_args = language.get_argument_types(rmode[0], rmode[1])
            arg_desc = []
            for t in range(rmode[1]):
                arg_mode = rmode[2][t]
                arg_type = type_args[t]
                arg_desc.append( (arg_mode, arg_type) )
                if arg_mode == '+':
                    if arg_type not in self.intype2func:
                        self.intype2func[arg_type] = set()
                    self.intype2func[arg_type].add(functor)
                elif arg_mode == 'c':
                    const_arg_key = functor+'_'+str(t)
                    vals = language.get_type_values(const_arg_key)
                    self.const_vals[const_arg_key] = vals
                else:   #if arg_mode == '-'
                    if functor not in self.out_args:
                        self.out_args[functor] = []
                    self.out_args[functor].append(t)

            self.funcsig[functor] = arg_desc         
    
    
    def _process_bg_program(self, bg_program):
        # This should be in rule_grounder. For now, We piggy back on prolog
        from pyswip import Prolog
        self._prolog = Prolog()
        self._prolog.consult(bg_program)
        return 
    
    @staticmethod
    def _extract_typed_args(term:Term):
        typed_args = set()
        for a in term.args:
            print(a)

    @staticmethod
    def _create_grounding_from_term(term:Term):
        # Use strings for now
        return str(term)

    def get_groundings_with_new_var(self, func, new_var, seen_vars):
        arg_type, arg_val = new_var
        arg_desc = self.funcsig[func]

        args_for_query = []
        groundings = []


        # matching_arg_type_indices = []
        # for i in range(len(arg_desc)):
        #     if arg_desc[i][1] == arg_type and arg_desc[i][0] == '+':
        #         matching_arg_type_indices.append(i)

        # multidict_safe_add(seen_vars, new_var[0], new_var[1])
        # for i in range(len(matching_arg_type_indices)):
        #     for arg_combination in argument_combinations(func, arg_desc, seen_vars, new_var):
        #         g = self._prolog.query(arg_combination)
        #         groundings.append(g)
        
        for arg_combination in argument_combinations(func, arg_desc, self.const_vals, seen_vars, new_var):                
            for g in self._prolog.query( term2pyswip(arg_combination) ): # arg_combination.repr):
                grounded = arg_combination.apply( {k: Constant(g[k]) for k in g} )# (g)     # Term(arg_combination.functor, *arg_combination.args)
                groundings.append(grounded)
        return groundings

    

    def _extract_typed_args(self, term:Term):
        sig = self.funcsig[term.functor]
        arg_vals = term.args

        typed_args = []
        for i in range(len(sig)):
            typed_args.append( (sig[i][1], arg_vals[i]) )
        
        return typed_args

    def derive_LHM_for_example(self, example: Example):
        # Assert all the facts in the example to the bg_program
        seen_vars = {}      # type:str -> set(val:str)
        new_vars = set()    # Tuple(type:str, val:str)
        # Add all grounded stuff. Add all values that come out of it to the free_fars
        lhm = set()
        
        lhm.add(self._create_grounding_from_term(example.classification_term))
        new_vars.update(self._extract_typed_args(example.classification_term))
        # Also, assert these facts
        for t in example.data:
            lhm.add(t)
            self._prolog.assertz(self._create_grounding_from_term(t))
            # And collect the new values
            # TODO: You are here    
            new_vars.update(self._extract_typed_args(t))
            
        
        # now we reach the main loop.
        # While we have args of types 
        while len(new_vars) > 0:
            # for nv in new_vars:
            nv = new_vars.pop()
            arg_type = nv[0]
            # We need to add it to seen_vars, so multiple instances can be used, 
            # but we also need to ensure we don't try groundings without new_var
            # Because we've already tried those. 
            # This is safe to do here.
            multidict_safe_add(seen_vars,nv[0] , nv[1])
            for func in self.intype2func.get(arg_type, []):
                new_groundings = self.get_groundings_with_new_var(func, nv, seen_vars)
                lhm.update(new_groundings)
                for t in new_groundings:
                    for out_arg_index in self.out_args[func]:
                        out_arg_type =  self.funcsig[func][out_arg_index][1]
                        out_arg_val = t.args[out_arg_index]
                        if out_arg_val not in seen_vars[out_arg_type]: # new_vars is a set, duplicates should be handled.
                            new_vars.add( (out_arg_type, out_arg_val) )
                        


    

            

        # for func_key in self.funcsig:
        #     func_val = self.funcsig[func_key]

        for t in example.data:
            self._prolog.retract(self._create_grounding_from_term(t))

        return lhm
        
def test_arg_combination_generator():
    signature = [ ('+', 'a'), ('+', 'b'), ('+', 'c'), ('+', 'a'), ('+', 'b'), ('-', 'd'), ('-', 'd') ]
    seen_vars = {
        'a' : {'a0', 'a1'},
        'b' : {'b0', 'b1', 'b2'},
        'c' : {'c0', 'c1', 'c2', 'c3'}
    }
    new_var = ('a', 'a_n')

    for ac in argument_combinations('f', signature, {}, seen_vars, new_var):
        print(ac)



def running_example_files():
    from os import path
    dir_path = path.join(path.dirname(path.abspath(__file__)), "test_files", "even_rules")
    S_FILE = path.join(dir_path, "even.s")
    KB_FILE = path.join(dir_path, "even.kb")
    BG_FILE = path.join(dir_path, "even.bg")
    return S_FILE, KB_FILE, BG_FILE

def parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE):
    
    from refactor.back_end_picking import get_back_end_default, QueryBackEnd
    from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
    from refactor.io.parsing_examples import KeysExampleBuilder
    from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
    from refactor.representation.example import InternalExampleFormat

    internal_ex_format = InternalExampleFormat.CLAUSEDB
    parsed_settings = KeysSettingsParser().parse(S_FILE)
    
    prediction_goal_handler = parsed_settings.get_prediction_goal_handler()  # type: KeysPredictionGoalHandler
    prediction_goal = prediction_goal_handler.get_prediction_goal()  # type: Term

    background_knowledge_wrapper \
    = parse_background_knowledge_keys(BG_FILE,
                                      prediction_goal)  # type: BackgroundKnowledgeWrapper

    full_background_knowledge_sp \
        = background_knowledge_wrapper.get_full_background_knowledge_simple_program()  # type: Optional[SimpleProgram]

    example_builder = KeysExampleBuilder(prediction_goal, False)
    training_examples_collection = example_builder.parse(internal_ex_format, KB_FILE,
                                                     full_background_knowledge_sp)  # type: ExampleCollection

    backend = get_back_end_default(QueryBackEnd.SIMPLE_PROGRAM)
    examples = backend.get_transformed_example_list(training_examples_collection)
    

    return parsed_settings, examples, full_background_knowledge_sp

def test_language_parsing():
    from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
    S_FILE, KB_FILE, BG_FILE = running_example_files()
    parsed_settings, examples, bg_sp = parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE)
    pred_goal = parsed_settings.get_prediction_goal_handler().get_prediction_goal()
    
    bgm = BackgroundManager(pred_goal, parsed_settings.language, BG_FILE)
    bgm.setup()

    print(bgm.funcsig)
    print(bgm.intype2func)
    print(bgm.const_vals)


def test_lhm():
    # NOT TESTED
    S_FILE, KB_FILE, BG_FILE = running_example_files()
    parsed_settings, examples, bg_sp = parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE)
    pred_goal = parsed_settings.get_prediction_goal_handler().get_prediction_goal()
    bgm = BackgroundManager(pred_goal, parsed_settings.language, BG_FILE)
    bgm.setup()

    for example in examples:
        print(bgm.derive_LHM_for_example(example))

def run_some_test():
    # test_arg_combination_generator()
    # test_language_parsing()
    test_lhm()


if __name__=='__main__':
    run_some_test()
