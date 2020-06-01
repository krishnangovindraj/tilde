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
        return self._compute_weighted_depth(example, self.tree)
        # return self._predict_recursive(example, self.tree, 1)

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


    def _compute_weighted_depth(self, example: Example, tree_node: TreeNode):
        if tree_node.is_leaf_node():
            return self.weights[tree_node]
        else:
            succeeds_test = self.test_evaluator.evaluate(example, tree_node.test)
            if succeeds_test:
                return self.weights[tree_node] + self._compute_weighted_depth(example, tree_node.left_child)
            else:
                return self.weights[tree_node] + self._compute_weighted_depth(example, tree_node.right_child)

    def dump_weights(self):
        self.weight_sum = 0
        dw = self._dump_weights_rec(self.tree)
        print("WEIGHT_SUM=%f v/s Expected=%f"%(self.weight_sum, self._expected_nodes_for_n_examples(self.subtree_examples[self.tree])))

        self.weight_sum = 0
        return dw

    def _dump_weights_rec(self, tree_node, cumulative_weight = 0, indent = ''):
        if tree_node.is_leaf_node():
            self.weight_sum += self.weights[tree_node] * self.subtree_examples[tree_node]
            return indent+ "%f[%d/%d](%f)"%(self.weights[tree_node], self.subtree_examples[tree_node], self.subtree_nodes[tree_node],  cumulative_weight + self.weights[tree_node])
        else:
            self.weight_sum += self.weights[tree_node]
            return '\n'.join([
                indent+str(self.weights[tree_node]),
                self._dump_weights_rec(tree_node.left_child, cumulative_weight + self.weights[tree_node], indent+'\t'), 
                self._dump_weights_rec(tree_node.right_child, cumulative_weight + self.weights[tree_node], indent+'\t')
            ])
