from typing import Set

from problog.logic import Term, Constant, Clause
from problog.program import LogicProgram

from refactor.utils import multidict_safe_add
from refactor.background_management.groundedkb.groundedkb import GroundedKB
from refactor.representation.language import TypeModeLanguage
from refactor.tilde_essentials.example import Example

class RuleInstance:
    def __init__(self, clause):
        self._clause = clause   # For debugging for now
        self.head = clause.head
        self.body = RuleInstance.flatten_body(clause.body)


    @staticmethod 
    def flatten_body(body):
        if body.functor == ',':
            bl = list(body.args)
            return  [bl[0]] + RuleInstance.flatten_body(bl[1])
        else:
            return [body]

    def __repr__(self):
        return "RuleInstance:[%s]"%str(self._clause)
        
    def __str__(self):
        return "RuleInstance:[%s]"%str(self._clause)

    def ground_head(self, subst):
        gh = Term(self.head.functor, *self.head.args)
        gh = gh.apply( {k : Constant(subst[k]) for k in subst})
        return gh


class PythonStoreForSubsumptionBasedGroundedKB(GroundedKB):

    def __init__(self, bg_program_sp: LogicProgram, language: TypeModeLanguage, prediction_goal_handler, max_lhm_iterations= 100):

        self._bg_program_sp = bg_program_sp
        self.language = language
        self.prediction_goal_handler = prediction_goal_handler

        self.max_lhm_iterations = max_lhm_iterations

        self.db = {}

        # Quick index to see which rules to retry when a new ground_fact is added.
        self.affected_list = {} 

        # A representation of the rules in the background knowledge & facts entailed
        self.rules = {}         # functor:str -> rule:?
        self.bg_groundings = set()    # functor: str -> list(term:?)
        
        # Index structures
        self.vars_to_bg_terms = None
        self.in_arg_indices = None  # Compulsory in arg. i.e., not +-
        self.out_arg_indices = None

    def add_fact(self, fact):
        self.bg_groundings.add(fact) 
        self._update_encoded_bg([fact])

    def query_fact(self, fact):
        return fact in self.bg_groundings
    
    def add_many_facts(self, facts):
        self.bg_groundings.update(facts)
        self._update_encoded_bg(facts)

    """ Cache an encoding of the DB to save effort during the theta subsumption step"""
    def _update_encoded_bg(self, facts):
        pass



    """ Derives groundings of `rule` entailed by the KB """
    def derive_groundings(self, rule):
        raise NotImplementedError("This is inefficient. If you really need it, Delete this raise statement and uncomment the code.")
        # Nothing to do really, just theta subsumption :p 
        # self.thetasubsumption(rule)
        

    """ Derives those groundings of `rule` entailed by (KB AND new_ground_fact) but not by KB alone """
    def derive_groundings_incremental(self, new_ground_fact : Term, db_extension: Set[Term]):
        gf_sig = (new_ground_fact.functor, new_ground_fact.arity)
        incremental_groundings = set()

        for rule in self.affected_list.get(gf_sig, set()):
             incremental_groundings.update(self.derive_groundings_for_rule_incremental(rule, new_ground_fact, db_extension))

        return incremental_groundings
    
            
    """ examples is _inout_, specifically example.data is updated for example in examples """
    def saturate_examples(self, examples):
        for example in examples:
            existing_facts = set(example.logic_program)
            lhm = self.derive_groundings_for_example(example)
            for t in lhm:
                if t not in existing_facts: # and t != example.classification_term:
                    example.logic_program.add_fact(t)
            existing_facts.update(lhm)
            if example.classification_term is not None:
                self._saturate_with_relevant_bg(example, existing_facts)
            #else: TODO

    def derive_groundings_for_example(self, example):
        db_extension = set()
        # Now for everything in example.data
        
        # example_data = Term.from_string(example.data).args[1].args
        
        pending_groundings = set(example.logic_program)
        derived_groundings = set()
        lhm_iterations = 0
        while len(pending_groundings) > 0:      # You're not seeing double.
            lhm_iterations += 1
            if lhm_iterations > self.max_lhm_iterations:
                raise Exception("_compute_bg_LHM has exceeded (configurable) iteration limit of " + self.max_lhm_iterations) 
            while len(pending_groundings) > 0:
                t = pending_groundings.pop()
                ng = self.derive_groundings_incremental(t, db_extension)
                derived_groundings.update(ng)
                db_extension.add(t)
            
            pending_groundings = [ d for d in derived_groundings if not (self.query_fact(d) or d in db_extension)]
            derived_groundings = set()

        return db_extension

    ###############
    # BG parsing #
    ##############
    def setup(self):
        self._process_bg_program(self._bg_program_sp)
        self._compute_bg_LHM()
        self._create_smart_saturation_indices()

    def _process_bg_rule(self, entry : Clause):
        rule = RuleInstance(entry)
        head_sig = (entry.head.functor, entry.head.arity)
        multidict_safe_add( self.rules, head_sig, rule )
        for b in rule.body:
            multidict_safe_add(self.affected_list, (b.functor, b.arity), rule)


    def _process_bg_program(self, bg_program_sp : LogicProgram):
        # This should be in rule_grounder. For now, We piggy back on prolog
        for entry in bg_program_sp:
            if type(entry) == Term:
                self.add_fact(entry)
            elif type(entry) == Clause:
                self._process_bg_rule(entry)
    
    #######################
    # grounding procedure #
    #######################    
    @staticmethod
    def new_groundfact_rename(term):
        return Term("newgroundfact__"+ term.functor, term.args)

    @staticmethod
    def generate_groundfactrenamed_bodies(body, groundfact):
        indices = [i for i in range(len(body)) if (body[i].functor,body[i].arity) == (groundfact.functor, groundfact.arity)]
        for i in range(1, 1 << len(indices)):
            body_frags = [b for b in body]
            for j in range(len(indices)):
                mask = 1 << j
                if i & mask:
                    body_frags[indices[j]] =  PythonStoreForSubsumptionBasedGroundedKB.new_groundfact_rename( body_frags[indices[j]] )
            yield body_frags


    """ Definitely not thread-safe by itself as db_extension is not read-only. """
    def _generate_groundings_incremental(self, rule : RuleInstance, groundfact : Term, __out__new_groundings : Set[Term], db_extension : Set[Term]):
        # Optimization - We can force the new groundfact to be used by renaming it to something unique,
        # and replacing atleast one of the occurences in the rule body to the unique name   
        
        renamed_groundfact =  self.new_groundfact_rename(groundfact)
        # Add this to db_extension, because that's what it is. Remove it later.
        db_extension.add(renamed_groundfact)

        subbed_heads = set() 
        for renamed_body_terms in self.generate_groundfactrenamed_bodies(rule.body, groundfact):
            substitutions = self.thetasubsumption(renamed_body_terms, db_extension)# [renamed_groundfact])
            subbed_heads.update(rule.ground_head(s) for s in substitutions)
        
        # Remove renamed_groundfact from db_extension
        db_extension.remove(renamed_groundfact)
        __out__new_groundings.update(subbed_heads)
    

    def derive_groundings_for_rule_incremental(self, rule : RuleInstance, new_ground_fact : Term, db_extension : Set[Term]):
        new_groundings = set()
        self._generate_groundings_incremental(rule, new_ground_fact, new_groundings, db_extension)

        return new_groundings

    def _compute_bg_LHM(self):
        empty_db_extension = set()

        pending_groundings = set(self.bg_groundings)
        derived_groundings = set()
        lhm_iterations = 0
        while len(pending_groundings) > 0:      # You're not seeing double.
            lhm_iterations += 1
            if lhm_iterations > self.max_lhm_iterations:
                raise Exception("_compute_bg_LHM has exceeded (configurable) iteration limit of " + self.max_lhm_iterations) 
            while len(pending_groundings) > 0:
                t = pending_groundings.pop()
                ng = self.derive_groundings_incremental(t, empty_db_extension)
                derived_groundings.update(ng)
                self.add_fact(t)
                
            newly_derived = [ d for d in derived_groundings if not self.query_fact(d)]
            # print("Newly derived: " + str(newly_derived))
            # self.add_many_facts(newly_derived)
            pending_groundings = newly_derived
            derived_groundings = set()

    def _create_smart_saturation_indices(self):
        # How do we handle constants? Treat them as a - variable.
        self.vars_to_bg_terms = {}
        self.in_arg_indices = {}
        self.out_arg_indices = {}
        self.const_arg_indices = {}
        for functor,arity,modes in self.language.get_refinement_modes():
            self.in_arg_indices[(functor, arity)] = [i for i in range(len(modes)) if '+' in modes[i]] # Following I now disagree with: + == instead of + in, because these are COMPULSORY in args
            self.out_arg_indices[(functor, arity)] = [i for i in range(len(modes)) if '-' in modes[i]]
            self.const_arg_indices[(functor, arity)] = [i for i in range(len(modes)) if 'c'==modes[i]]

        for fact in self.bg_groundings:
            if (fact.functor, fact.arity) in self.in_arg_indices:
                for arg in [fact.args[i] for i in self.in_arg_indices[(fact.functor, fact.arity)]]:
                    if arg not in self.vars_to_bg_terms:
                        self.vars_to_bg_terms[arg] = set()
                    self.vars_to_bg_terms[arg].add(fact)

    def _saturate_with_relevant_bg(self, example: Example, existing_facts: Set[Term]):
        prediction_goal_index = self.prediction_goal_handler.get_predicate_goal_index_of_label_var()

        pending_args = set()
        completed_args = set()
        for i,arg in enumerate(example.classification_term.args):
            if i != prediction_goal_index:
                pending_args.add(arg)

        # Also add all the args in existing_facts
        # TODO: This doesn't consider whether they're in args or out_args. Should it?
        pending_args.update(arg for t in existing_facts for arg in t.args)

        args_remaning = {}
        while len(pending_args) > 0:
            arg = pending_args.pop()
            for term in self.vars_to_bg_terms.get(arg, []):
                if term in existing_facts:
                    continue

                if term not in args_remaning:
                    in_args = set(term.args[i] for i in self.in_arg_indices[(term.functor, term.arity)])
                    args_remaning[term] = [t for t in in_args if t not in completed_args]

                if arg in args_remaning[term]:
                    args_remaning[term].remove(arg)

                    if len(args_remaning[term]) == 0:
                        example.logic_program.add_fact(term)
                        existing_facts.add(term)
                        out_args = [term.args[i] for i in range(len(term.args))
                            if i in self.out_arg_indices[(term.functor, term.arity)]
                            or i in self.const_arg_indices[(term.functor, term.arity)]]
                        new_args = [a for a in out_args if (a not in completed_args and a not in pending_args and a!=arg)]
                        pending_args.update(new_args)

            completed_args.add(arg)

    ###############################
    # Theta-subsumption abstracts #
    ###############################
    """ Must return a dictionary of substitutions which can be used by problog.logic.Term.apply """
    def thetasubsumption(self, rule, db_extension=set()):
        raise NotImplementedError("Abstract method")
