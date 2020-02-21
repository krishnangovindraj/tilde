from itertools import product
from typing import List

from problog.logic import Term

from .TILDE_query import TILDEQuery
from .lookahead_mode import LookaheadMode


class LookaheadExtensionGenerator:

    def __init__(self, query: TILDEQuery, base_term: Term, language, max_depth : int ):
        self.query = TILDEQuery(query, base_term)
        self.base_term = base_term
        self.language = language
        self._max_depth = max_depth
    
    def _get_fixed_args_and_refinement_mode(self, candidate, extension_template):
        flat_args = LookaheadMode.flatten_args([extension_template])
        fixed_args = {i : flat_args[i] for i in range(len(flat_args)) if flat_args[i] != LookaheadMode.PLACEHOLDER_VAR}
        # TODO: Caching
        arg_mode = None
        for rf in self.language.get_refinement_modes():
            if rf[0] == extension_template.functor and rf[1] == extension_template.arity:
                arg_mode = rf[2]
                break
        
        if arg_mode is None:
            raise ValueError("Lookahead extension " + str(extension_template) + " has unknown refinement mode")
        
        return fixed_args, arg_mode
    
    def generate_extensions(self):
        nb_of_vars_in_query = len(self.query.get_variables())
        
        variables_in_query_by_type = self.language.get_variable_types(*self.query.get_literals()).copy()  # type: Dict[TypeName, List[Term]]
        
        if self.query.get_literal() is not None:
            already_generated_literals = self.query.get_literal().refine_state.copy()
        else:
            already_generated_literals = set()

        for y in self._generate([self.base_term], already_generated_literals, variables_in_query_by_type, nb_of_vars_in_query, 1):
            yield LookaheadMode.list_to_conjunction(y)

    def _generate(self, conj_to_extend, already_generated_literals, variables_in_query_by_type, nb_of_vars_in_query, depth):
        from .language import TypeModeLanguage
        
        var_renamer = TypeModeLanguage.ReplaceNew(nb_of_vars_in_query)
        suffix = [t for t in conj_to_extend]
        while len(suffix) > 0:
            sig = LookaheadMode.get_sig(suffix)
            for candidate in self.language._lookahead[sig]:
                if candidate.matches_pattern(suffix):
                    extension_template = candidate.get_extension_for_term(suffix)
                    # We still have to consider the arguments not specified by the lookahead description
                    fixed_args, arg_mode_indicators = self._get_fixed_args_and_refinement_mode(candidate, extension_template)
                    extension_arg_table = self.language._get_possible_term_arguments_for(extension_template.functor, arg_mode_indicators, variables_in_query_by_type, fixed_args)
                    for extension_args in product(*extension_arg_table):
                        generated_literal = Term(extension_template.functor, *extension_args)
                        if generated_literal in already_generated_literals:
                            continue
                        already_generated_literals.add(generated_literal)
                        extension = generated_literal.apply( var_renamer )
                        if extension in already_generated_literals:
                            continue
                        extended_conj = suffix + [extension]
                        yield extended_conj
                        
                        # Do we need to recurse?
                        if depth < self._max_depth:
                            self._generate(extended_conj, already_generated_literals, variables_in_query_by_type, var_renamer.count, depth+1)
                        
                        # cleanup
                        already_generated_literals.remove(generated_literal)
            suffix.pop()
        # Should be done
