from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_node import TreeNode
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.example import Example 

class IsolationTree(DecisionTree):

    def __init__(self):
        self.tree = None  # type: Optional[TreeNode]
        self.tree_builder = None  # type: Optional[TreeBuilder]
        self.test_evaluator = None  # type: Optional[TestEvaluator]
        self.tree_pruner = None

        self.subtree_nodes = None
        self.subtree_examples = None
        self.weights = None

    """ Returns the height of the [null] node which the example is sorted to """
    def predict(self, example):
        return self._leaf_path_length( example, self.tree )

    def fit(self, examples, tree_builder: TreeBuilder):
        super().fit(examples, tree_builder)

        self.subtree_nodes = {}
        self.subtree_examples = {}

    def _expected_nodes_for_n_examples(self, n_examples):
        return max(0,2*n_examples - 1)

    def _c(self, n):
        from math import log # ln
        return 2 * (log(n-1) + 0.5772156649) - (2*(n-1)/n)


    # This is what I normalize against and is to demonstrate the issues with no-normalizations in sparse split-spaces
    def _leaf_path_length(self, example: Example, tree_node: TreeNode):
        if tree_node.is_leaf_node():
            return 1 + (self._c(len(tree_node.examples)) if len(tree_node.examples) > 1 else 0)
        else:
            if tree_node.left_child.is_leaf_node() and len(tree_node.left_child.examples) == 0:
                my_weight = 0
            elif tree_node.right_child.is_leaf_node() and len(tree_node.right_child.examples) == 0:
                my_weight = 0
            else:
                my_weight = 1
            
            succeeds_test = self.test_evaluator.evaluate(example, tree_node.test)
            if succeeds_test:
                return my_weight + self._leaf_path_length(example, tree_node.left_child)
            else:
                return my_weight + self._leaf_path_length(example, tree_node.right_child)

    def explain(self, example, tree_node):
        if tree_node.is_leaf_node():
            return [], 0
        else:
            succeeds_test = self.test_evaluator.evaluate(example, tree_node.test)
            if succeeds_test:
                query_tail, leaf_depth = self.explain(example, tree_node.left_child)
                return [str(tree_node.test.tilde_query.get_literal())] + query_tail , leaf_depth+1
            else:
                query_tail , leaf_depth = self.explain(example, tree_node.right_child)
                return ["fail(%s)"%(str(tree_node.test.tilde_query.get_literal()))]  + query_tail , leaf_depth+1

