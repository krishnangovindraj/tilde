from random import choices as random_choices 

from refactor.tilde_essentials.destuctable import Destructible
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.tree_node import TreeNode

from refactor.tilde_essentials.tree import DecisionTree

# TODO: Everything here.


class RandomForest(Destructible):
    """
    Decision tree used for making predictions. Initially empty.
    An internal TreeNode tree is fitted on training examples using a TreeBuilder.

    """

    def __init__(self, n_trees, resample_size):
        self.trees = None
        self.tree_builder = None  # type: Optional[TreeBuilder]
        self.test_evaluator = None  # type: Optional[TestEvaluator]
        self.tree_pruner = None

        self.n_trees = n_trees
        self.resample_size = resample_size

    def fit(self, examples, tree_builder: TreeBuilder):
        self.tree_builder = tree_builder
        self.test_evaluator = self.tree_builder.splitter.test_evaluator
        self.trees = [self._build_one_tree(examples, tree_builder) for _ in range(self.n_trees)]

    def _build_one_tree(self, examples, tree_builder: TreeBuilder) -> DecisionTree:
        resampled_examples = random_choices(examples, k=self.resample_size)
        decision_tree = DecisionTree()
        decision_tree.fit(resampled_examples, tree_builder)
        return decision_tree

    def predict(self, example):
        from collections import Counter
        all_predictions = [tree.predict(example) for tree in self.trees]

        # TODO: Other combination techniques?
        count_dict = Counter(all_predictions)
        highest_count, majority_class = max( ((count_dict[k],k) for k in count_dict), key= lambda x: x[0] )
        return majority_class

    def __str__(self):
        return self.tree.__str__()

    def destruct(self):
        for t in self.trees:
            t.destruct()

    def __str__(self):
        return  '\n'.join( "---\nTree[%d]\n%s\n---\n"%(i, str(t)) for i, t in enumerate(self.trees))   

def write_out_tree(fname: str, tree: DecisionTree):
    # write out tree
    print('\t--- writing out tree to: ' + fname)
    with open(fname, 'w') as f:
        f.write(str(tree))
