from random import choices as random_choices 

from refactor.tilde_essentials.destuctable import Destructible
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_node import TreeNode

from refactor.tilde_essentials.tree import DecisionTree

class IsolationForest:
    def __init__(self, n_trees):
        self.n_trees = n_trees
        self._trees_left = 0

    def fit(self, examples, tree_builder: TreeBuilder):
        self.tree_builder = tree_builder
        self.test_evaluator = self.tree_builder.splitter.test_evaluator
        
        self._trees_left = self.n_trees
        self.trees = [self._build_one_tree(examples, tree_builder) for _ in range(self.n_trees)]

    def _build_one_tree(self, examples, tree_builder: TreeBuilder) -> DecisionTree:
        decision_tree = DecisionTree()
        decision_tree.fit(examples, tree_builder)
        self._trees_left -= 1

        if self._trees_left % (self.n_trees/10)==0:
            print("Built ~%d%% of trees"%( 100*(1-float(self._trees_left)/self.n_trees)))
        # print("--- %d left --"%self._trees_left)
        return decision_tree

    def get_length_distribution(self, examples):
        dist = {e: [] for e in examples}
        for t in self.trees:
            len_dict = {}
            self._get_example_branch_lengths(t.tree, examples, len_dict)
            for e in examples:
                dist[e].append(len_dict[e])
        return dist

    def _get_example_branch_lengths(self, tree: TreeNode, examples, len_dict):
        if tree.is_leaf_node():
            for e in tree.examples:
                len_dict[e] = tree.depth
        else:
            self._get_example_branch_lengths(tree.left_child, examples, len_dict)
            self._get_example_branch_lengths(tree.right_child, examples, len_dict)

    def prune(self, pruning_function):
        pass # No prune. Only build >:(

    def destruct(self):
        for t in self.trees:
            t.destruct()

    def __str__(self):
        return  '\n'.join( "---Tree[%d]---\n%s\n\n"%(i, str(t)) for i, t in enumerate(self.trees))

class ResultStoringIsolationForest(IsolationForest):
    def __init__(self, n_trees):
        super().__init__(n_trees)

    def fit(self, examples, tree_builder):
        super().fit(examples, tree_builder)
        ld = self.get_length_distribution(examples)
        self.stored_length_distribution = {e.classification_term: ld[e] for e in ld}
