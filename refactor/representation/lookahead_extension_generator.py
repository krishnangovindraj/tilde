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
    
    def _add_new_variables_in_term_by_type(self, generated_literal, extension, arg_types, variables_in_query_by_type):
        added_vars = set()
        for i in range(len(extension.args)):
            if extension.args[i] != generated_literal.args[i]:
                added_vars.add( (arg_types[i], extension.args[i]) )
                variables_in_query_by_type[arg_types[i]].add(extension.args[i])
        return added_vars 

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
        freshly_generated_literals = set()
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
                        freshly_generated_literals.add(generated_literal)
                        already_generated_literals.add(generated_literal)
                        extension = generated_literal.apply( var_renamer )
                        # TODO: I'm unsure why I have two tests for this, but I ran into a collission.
                        # So I'm adding the extension != generated_literal check
                        if extension != generated_literal and extension in already_generated_literals:
                            continue
                        extended_conj = conj_to_extend + [extension]
                        yield extended_conj
                        
                        # Do we need to recurse?
                        if depth < self._max_depth:
                            arg_types = self.language.get_argument_types(extension.functor, extension.arity)
                            
                            added_type_vars = self._add_new_variables_in_term_by_type(generated_literal, extension, arg_types, variables_in_query_by_type)
                            for la in self._generate(extended_conj, already_generated_literals, variables_in_query_by_type, var_renamer.count, depth+1):
                                yield la

                            for (arg_type, var_name) in added_type_vars:
                                variables_in_query_by_type[arg_type].remove(var_name)

            suffix.pop(0) # We pop the first element
        # cleanup
        for g in freshly_generated_literals:
            already_generated_literals.remove(g)
