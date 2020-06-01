from random import choices as random_choices 

from refactor.tilde_essentials.destuctable import Destructible
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_node import TreeNode

#from refactor.tilde_essentials.tree import DecisionTree
from refactor.random_forest.isolation_tree import IsolationTree


class IsolationForest:
    def __init__(self, n_trees, resample_size=0):
        self.n_trees = n_trees
        self.n_examples = 0
        self._trees_left = 0
        self.resample_size = resample_size

    def fit(self, examples, tree_builder: TreeBuilder):
        self.n_examples = len(examples)
        self.tree_builder = tree_builder
        self.test_evaluator = self.tree_builder.splitter.test_evaluator

        self._trees_left = self.n_trees
        self.trees = [self._build_one_tree(examples, tree_builder) for _ in range(self.n_trees)]

    def _build_one_tree(self, examples, tree_builder: TreeBuilder) -> IsolationTree:

        resample_size = self.resample_size if self.resample_size > 0 else len(examples)
        resampled_examples = random_choices(examples, k=resample_size)
        # resampled_examples = examples

        decision_tree = IsolationTree()
        decision_tree.fit(resampled_examples, tree_builder)
        self._trees_left -= 1

        if self._trees_left % (self.n_trees/10)==0:
            print("Built ~%d%% of trees"%( 100*(1-float(self._trees_left)/self.n_trees)))
        # print("--- %d left --"%self._trees_left)
        return decision_tree

    def _c(self, n):
        from math import log # ln
        return 2 * (log(n-1) + 0.5772156649) - (2*(n-1)/n)

    def predict(self, example):
        from math import pow
        def anomaly_score(heights, n_examples):
            avg_height = sum(heights)/len(heights)
            pp = avg_height/self._c(self.n_examples)
            return pow(2, -pp)

        heights = []
        for t in self.trees:
            heights.append( t.predict(example) )

        return anomaly_score(heights, self.n_examples), heights

    def get_training_example_length_distribution(self, examples):
        dist = {e: [] for e in examples}
        for t in self.trees:
            len_dict = {}
            self._get_example_branch_lengths(t.tree, examples, len_dict)
            for e in examples:
                dist[e].append(len_dict[e])
        return dist

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
