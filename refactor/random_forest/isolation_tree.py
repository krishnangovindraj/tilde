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
        self.HAX_PREDICTING_NODE = {} # Example -> TreeNode


    """ Returns the height of the [null] node which the example is sorted to """
    def predict(self, example):
        return self.pred_function( example, self.tree )

    def fit(self, examples, tree_builder: TreeBuilder):
        super().fit(examples, tree_builder)

        self.subtree_nodes = {}
        self.subtree_examples = {}

        self._compute_subtree_examples(self.tree)
        self.weights = {}
        self.compute_node_weights_recursive(self.tree, self._expected_nodes_for_n_examples(self.subtree_examples[self.tree]))

    def _expected_nodes_for_n_examples(self, n_examples):
        return max(0,2*n_examples - 1)

    def _compute_subtree_examples(self, tree_node):
        if tree_node.is_leaf_node():
            self.subtree_nodes[tree_node] = self._expected_nodes_for_n_examples(len(tree_node.examples)) # Total nodes for tree_node.examples leaves
            self.subtree_examples[tree_node] = len(tree_node.examples)
        else:
            self._compute_subtree_examples(tree_node.left_child)
            self._compute_subtree_examples(tree_node.right_child)
            self.subtree_nodes[tree_node] = 1 + self.subtree_nodes[tree_node.left_child] + self.subtree_nodes[tree_node.right_child]
            self.subtree_examples[tree_node] = self.subtree_examples[tree_node.left_child] + self.subtree_examples[tree_node.right_child]

    def compute_node_weights_recursive(self, tree_node, subtree_weight):
        n_examples = self.subtree_examples[tree_node]

        if tree_node.is_leaf_node():
            # weight has to account for the extended path
            if n_examples == 0:
                self.weights[tree_node] = 0
            else:
                if n_examples > 1:
                    # The +1 is important because c(2) is apparently 0. something . What even?
                    effective_further_depth = 1 + self._c( n_examples ) #  (1 + self._c(n_examples)-1)
                else:
                    effective_further_depth = 1
                self.weights[tree_node] = subtree_weight/n_examples # effective_further_depth * subtree_weight/self.subtree_nodes[tree_node]

        else:
            # Recurse
            lc_expected_size = self._expected_nodes_for_n_examples(self.subtree_examples[tree_node.left_child])
            rc_expected_size = self._expected_nodes_for_n_examples(self.subtree_examples[tree_node.right_child])

            self.weights[tree_node] = subtree_weight/self.subtree_nodes[tree_node]

            lc_subtree_weight = (subtree_weight-self.weights[tree_node]) * lc_expected_size/(lc_expected_size+rc_expected_size)
            rc_subtree_weight = (subtree_weight-self.weights[tree_node]) * rc_expected_size/(lc_expected_size+rc_expected_size)
            self.compute_node_weights_recursive(tree_node.left_child, lc_subtree_weight)
            self.compute_node_weights_recursive(tree_node.right_child, rc_subtree_weight)

    def _c(self, n):
        from math import log # ln
        return 2 * (log(n-1) + 0.5772156649) - (2*(n-1)/n)


    # This is what I normalize against and is to demonstrate the issues with no-normalizations in sparse split-spaces
    def _predict_non_weighted(self, example: Example, tree_node: TreeNode):
        if tree_node.is_leaf_node():
            from math import log2
            # return 1 +  log2(len(tree_node.examples))
            return 1 + (self._c(len(tree_node.examples)) if len(tree_node.examples) > 1 else 0)
        else:
            succeeds_test = self.test_evaluator.evaluate(example, tree_node.test)
            if succeeds_test:
                return 1 + self._predict_non_weighted(example, tree_node.left_child)
            else:
                return 1 + self._predict_non_weighted(example, tree_node.right_child)


    # This is what I normalize against and is to demonstrate the issues with no-normalizations in sparse split-spaces
    def pred_function(self, example: Example, tree_node: TreeNode):
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
                return my_weight + self.pred_function(example, tree_node.left_child)
            else:
                return my_weight + self.pred_function(example, tree_node.right_child)

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

