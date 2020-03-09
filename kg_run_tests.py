import unittest
from contextlib import redirect_stdout
from io import StringIO as io_StringIO

from kg_main import main as run_kg_main

DEFAULT_TEST_BACKEND = 'problog-simple' # 'subtle' # 'django'

def _encode_test(test):
    from refactor.query_testing_back_end.subtle.query_wrapping import SubtleQueryWrapper
    from refactor.query_testing_back_end.django.django_wrapper.ClauseWrapper import HypothesisWrapper
    from refactor.representation.TILDE_query import TILDEQuery
    
    # TODO: Write a get_query method for each wrapper. Introduce a wrapper for problog.
    tilde_query = None
    if isinstance(test, SubtleQueryWrapper):
        tilde_query = test.tilde_query
    elif isinstance(test, HypothesisWrapper):
        tilde_query = test._prolog_hypothesis
    elif isinstance(test, TILDEQuery):
        tilde_query = test
    
    return str(tilde_query.literal)

def _encode_tree(tree):
    if tree.is_leaf_node():
        el = None
        er = None
        encoded_info = tree.leaf_strategy.encode_to_tuple()
    else:
        el = _encode_tree(tree.left_child)
        er = _encode_tree(tree.right_child)
        encoded_info = _encode_test(tree.test)
    
    return ( (encoded_info), el, er)


def _run_test(argv):
    f = io_StringIO()
    with redirect_stdout(f):
        tree = run_kg_main(argv)

    return tree

class TestRegressionTrees(unittest.TestCase):

    def test_noisy_lines(self):
        expected_tree = (
            'divides(A,2)', 
                ((2303.8, 1.77), None, None),
                ('divides(A,5)', 
                    ((1224.84, 0.96), None, None), 
                    ('divides(A,3)', 
                        ((8.64, 0.44), None, None), 
                        ((289.48, 0.55), None, None)
                    )
                )
        )

        decision_tree = _run_test(['TestRegressionTrees__test_noisy_lines', 'test_datasets/regression/noisy_lines/config.json', DEFAULT_TEST_BACKEND])
        
        self.assertEqual(expected_tree, _encode_tree(decision_tree.tree), "Tree mismatch")

if __name__ == '__main__':
    unittest.main()
    pass
