from typing import Optional

import problog
from problog.engine import GenericEngine, DefaultEngine, ClauseDB
from problog.logic import Term, Var
from problog.program import LogicProgram, SimpleProgram, PrologString

from refactor.representation.example import ExampleWrapper
from refactor.query_testing_back_end.problog.query_wrapping import ProblogQueryWrapper
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.representation.TILDE_query import TILDEQuery


class ProbLogQueryEvaluator(TestEvaluator):
    def evaluate(self, instance, test) -> bool:
        raise NotImplementedError('abstract method')

    def __init__(self, engine: GenericEngine = None):
        if engine is None:
            self.engine = DefaultEngine()
            self.engine.unknown = 1
        else:
            self.engine = engine
        self.to_query = Term('to_query')


class SimpleProgramQueryEvaluator(ProbLogQueryEvaluator):
    def __init__(self,
                 background_knowledge: Optional[LogicProgram] = None,
                 engine: GenericEngine = None):
        super().__init__(engine=engine)
        if background_knowledge is None:
            self.db = self.engine.prepare(SimpleProgram())  # type: ClauseDB
        else:
            self.db = self.engine.prepare(background_knowledge)  # type: ClauseDB

        self.db += Term('query')(self.to_query)

    def evaluate(self, instance: Example, test: QueryWrapper) -> bool:

        query_conj = test.external_representation

        db_to_query = self.db.extend()

        for statement in instance.data:
            db_to_query += statement

        # TODO: remove ugly hack
        if hasattr(instance,  'classification_term') and instance.classification_term is not None:
            db_to_query += instance.classification_term

        db_to_query += (self.to_query << query_conj)

        query_result = problog.get_evaluatable().create_from(db_to_query, engine=self.engine).evaluate()

        return query_result[self.to_query] > 0.5

    def wrap_query(self, tilde_query: TILDEQuery):
        return ProblogQueryWrapper(tilde_query, tilde_query.to_conjunction())

    def transform_example(self, example_wrapper: ExampleWrapper) -> Example:
        classification_term = example_wrapper.classification_term if hasattr(example_wrapper, 'classification_term') else None
        example = Example(example_wrapper.logic_program, example_wrapper.label, classification_term)
        example.classification_term = example_wrapper.classification_term
        return example


if __name__ == '__main__':
    instance = Example(PrologString("""
    color(blue).
    taste(sweet).
    texture(fruity).
    
    """), None)
    query = TILDEQuery(None, Term('color')(Var('X')))

    evaluator = SimpleProgramQueryEvaluator()

    result = evaluator.evaluate(instance, evaluator.wrap_query(query))
    print(result)
