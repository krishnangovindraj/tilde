import unittest
from contextlib import redirect_stdout
from io import StringIO as io_StringIO

from kg_main import main as run_kg_main
from refactor.tilde_config import TildeConfig

from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.tilde_essentials.tree_node import TreeNode

DEFAULT_TEST_BACKEND = 'PROBLOG' # 'SUBTLE' # 'DJANGO'

def _encode_test(test: QueryWrapper) -> str:
    tilde_query = test.tilde_query
    return str(tilde_query.literal)

def _encode_tree(tree: TreeNode) -> str:
    if tree.is_leaf_node():
        el = None
        er = None
        encoded_info = tree.leaf_strategy.encode_to_tuple()
    else:
        el = _encode_tree(tree.left_child)
        er = _encode_tree(tree.right_child)
        encoded_info = (_encode_test(tree.test),)

    return ( (encoded_info), el, er)


def _run_test(argv, model_options=None):
    f = io_StringIO()
    with redirect_stdout(f):
        tree = run_kg_main(argv)
    return tree

class TestRegressionTrees(unittest.TestCase):

    def test_noisy_lines(self):
        expected_tree = \
            (('divisible_by(A,2)',),
                ((2303.8, 1.77), None, None),
                (('divisible_by(A,5)',),
                    ((1224.84, 0.96), None, None),
                    (('divisible_by(A,3)',),
                        ((8.64, 0.44), None, None),
                        ((289.48, 0.55), None, None)
                    )
                )
        )

        decision_tree = _run_test(['TestRegressionTrees__test_noisy_lines', 'test_datasets/regression/noisy_lines/config.json', DEFAULT_TEST_BACKEND])

        self.assertEqual(_encode_tree(decision_tree.tree), expected_tree, "Tree mismatch")


class TestRules(unittest.TestCase):

    def test_divisibility_six(self):
        # Sorry but my example sux. There are 2 possible trees. div4 might not have this problem.
        expected_tree_1 = \
            (('divides(A,3,C)',),
                (('divides(A,2,D)',),
                    (('pos', [('pos', '1.0')]), None, None),
                    (('neg', [('neg', '1.0')]), None, None)
                ),
                (('neg', [('neg', '1.0')]), None, None)
            )

        expected_tree_2 = \
            (('divides(A,3,C)',),
                (('divides(C,2,D)',),
                    (('pos', [('pos', '1.0')]), None, None),
                    (('neg', [('neg', '1.0')]), None, None)
                ),
                (('neg', [('neg', '1.0')]), None, None)
            )

        decision_tree = _run_test(['TestRules__test_divisibility_six', 'test_datasets/rules/divisibility_six/config.json', DEFAULT_TEST_BACKEND])

        self.assertIn(_encode_tree(decision_tree.tree), [expected_tree_1, expected_tree_2],"Tree mismatch")

    def test_squares(self):
        expected_tree = \
            (('divides(A,C,D), unify(C,D)',),
                (('pos', [('pos', '1.0')]), None, None),
                (('neg', [('neg', '1.0')]), None, None)
            )
        decision_tree = _run_test(['TestRules__test_squares', 'test_datasets/rules/squares/config.json', DEFAULT_TEST_BACKEND])

        self.assertEqual(_encode_tree(decision_tree.tree), expected_tree, "Tree mismatch")

class TestNumericalAttributes(unittest.TestCase):

    def test_onedimensional_range_exact(self):
        expected_tree = \
            (('realnum_x_leq(A,10)',),
                (('realnum_x_leq(A,5)',),
                    (('pos', [('pos', '1.0')]), None, None),
                    (('neg', [('neg', '1.0')]), None, None)),
                (('pos', [('pos', '1.0')]), None, None)
            )

        decision_tree = _run_test(['TestNumericalAttributes__test_onedimensional_range_exact', 'test_datasets/numerical/onedimensional_range/config.json', DEFAULT_TEST_BACKEND])
        self.assertEqual(_encode_tree(decision_tree.tree), expected_tree, "Tree mismatch")

class TestIsolationForest(unittest.TestCase):

    def test_gaussian2d_outliers(self):
        min_outliers_to_pass, actual_outliers, in_how_many = 7, 10, 12
        test_passed = False
        max_tries = 2
        print("---Start test_gaussian2d_outliers. This may take a minute ---")
        while not test_passed and max_tries > 0:
            max_tries-=1
            from refactor.model_factory import ModelFactory
            isolation_forest_options = ModelFactory.IsolationForestOptions(20, 5, 5)

            isolation_forest = _run_test(['TestIsolationForest__test_gaussian2d_outliers', 'test_datasets/isolation/gaussian/config.json', DEFAULT_TEST_BACKEND], isolation_forest_options)
            length_dist = isolation_forest.stored_length_distribution

            topK = sorted([(sum(length_dist[k]),str(k)) for k in length_dist])[:in_how_many]
            # print(topK)
            test_passed = len([ct for ct in topK if 'pos' in ct[1]]) >= min_outliers_to_pass
            if not test_passed:
                print("test_gaussian2d_outliers failed. Trying again, since this is probabilistic!")

        self.assertTrue(test_passed)

if __name__ == '__main__':
    unittest.main()
