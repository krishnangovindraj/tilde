from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_node import TreeNode

class IsolationTree(DecisionTree):

    def __init__(self):
        self.tree = None  # type: Optional[TreeNode]
        self.tree_builder = None  # type: Optional[TreeBuilder]
        self.test_evaluator = None  # type: Optional[TestEvaluator]
        self.tree_pruner = None
        self.HAX_PREDICTING_NODE = {} # Example -> TreeNode


    """ Returns the height of the [null] node which the example is sorted to """
    def predict(self, example):
        return self._predict_recursive(example, self.tree, 1)
    

    def _c(self, n):
        from math import log
        return 2 * (log(n-1) + 0.5772156649) - (2*(n-1)/n)


    def _predict_recursive(self, example, tree_node: TreeNode, depth: int):
        if tree_node.is_leaf_node():
            insperability_penalty = self._c(len(tree_node.examples))-1 if len(tree_node.examples) > 1 else 0
            return depth + insperability_penalty
        else:
            succeeds_test = self.test_evaluator.evaluate(example, tree_node.test)
            if succeeds_test:
                return self._predict_recursive(example, tree_node.left_child, depth+1)
            else:
                return self._predict_recursive(example, tree_node.right_child, depth+1)
