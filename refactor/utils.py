import warnings
import functools

import time

import sys
import os


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    return new_func


class Timer:
    def __init__(self, name=None):
        self.name = name
        self.start_time = None
        self.end_time = None

    def start(self) -> None:
        self.start_time = time.time()

    def end(self) -> float:
        self.end_time = time.time()
        return self.end_time


def block_all_printouts():
    sys.stdout = open(os.devnull, "w")


def enable_printouts():
    sys.stdout = sys.__stdout__

def multidict_safe_add(d, k, v, value_collection_type=set):
    if k not in d:
        d[k] = value_collection_type()
    d[k].add(v)


# Confusion matrix

from typing import Dict, List
from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_node import TreeNode
def training_accuracy(tree: DecisionTree):
    cm = training_confusion_matrix(tree)
    return (cm[0][0] + cm[1][1]) / (cm[0][0] + cm[1][1] + cm[0][1] + cm[1][0])

def confusion_matrix(truth, predictions):
    keys = sorted(list(set(str(t) for t in truth)))
    ccm = {}
    for t,p in zip(map(str,truth), map(str,predictions)):
        ccm[(t,p)] = ccm.get((t,p),0) + 1
    mat = [[0 for i in keys] for j in keys]
    for i,k1 in enumerate(keys):
        for j,k2 in enumerate(keys):
            mat[i][j] = ccm.get((k1,k2),0)

    return keys, mat


def training_confusion_matrix(tree: DecisionTree):
    ccm = _training_confusion_matrix_recursive(tree.tree)
    keys = sorted(list(set([k[0] for k in ccm] + [k[1] for k in ccm])))

    mat = [[0 for i in keys] for j in keys]
    for i,k1 in enumerate(keys):
        for j,k2 in enumerate(keys):
            mat[i][j] = ccm.get((k1,k2),0)

    return keys, mat

def _training_confusion_matrix_recursive(root: TreeNode):
    if root.is_leaf_node():
        return { (str(k),str(root.leaf_strategy.majority_label)): root.leaf_strategy.label_counts[k] for k in root.leaf_strategy.label_counts}
    else:
        lcm = _training_confusion_matrix_recursive(root.left_child)
        rcm = _training_confusion_matrix_recursive(root.right_child)
        keys = set(lcm.keys())
        keys.update(rcm.keys())
        return { k: lcm.get(k,0) + rcm.get(k,0) for k in keys }

def print_confusion_matrix(legend, matrix):
    FIRST_COL_WIDTH = 11
    WIDTH = 7
    def _pad_string(what, width=WIDTH, pad_char = ' '):
        return str(what).center(width, pad_char)

    def _format_row(first_col, rest_cols):
        return "|%s|%s|"%(
            _pad_string(first_col, FIRST_COL_WIDTH),
            '|'.join( map( _pad_string, rest_cols) )
        )

    sep = "-" * (FIRST_COL_WIDTH + 1 + (WIDTH + 1) * len(legend))
    print(sep)
    print(_format_row("Real\\Pred", legend))
    print(sep)
    for key,row in zip(legend, matrix):
        print( _format_row(key, row) )
        print(sep)
    print()

# Model summary printing 

def print_model_summary(model, examples):
    from refactor.random_forest.random_forest import RandomForest
    from refactor.random_forest.isolation_forest import IsolationForest
    from refactor.tilde_essentials.tree import DecisionTree
    
    if isinstance(model, IsolationForest):
        _print_isolation_forest_summary(model, examples)
    elif isinstance(model, RandomForest):
        _print_random_forest_summary(model, examples)
    elif isinstance(model, DecisionTree):
        _print_decision_tree_summary(model, examples)
    else:
        print("Unrecognized model type:" + type(model) )

def _print_isolation_forest_summary(model: 'IsolationForest', examples:'List[Example]'):
    topk = len(examples) # 10
    dist = {}
    score = {}
    for e in examples:
        score[e] = model.predict(e)
        # score[e], distances = model.predict(e)
        # dist[e] = distances

    # dist = model.get_length_distribution(examples)
    # for t in model.trees: print(t)
    # for e in examples :
    #     print("%s[%f]: %s"%(str(e.classification_term), score[e],  str([round(x,3) for x in dist[e]])))

    sorted_examples = sorted(examples, key=lambda e: score[e], reverse=True)
    triple = [(str(i+1), str(round(score[e],3)), str(e.classification_term) ) for i,e in enumerate(sorted_examples)]
    sorted_triple = triple # sorted(triple)
    print("Printing top-%d out of %d"%(topk, len(examples)))
    print("Rank\tScore\tKey")
    for st in sorted_triple:
        print('\t'.join(st))
    # for e in sorted_examples[:topk]:
    #     print("%s[%f]"%(str(e.classification_term), score[e]))


def _print_random_forest_summary(model: 'RandomForest', examples:'List[Example]'):
    from refactor.utils import confusion_matrix, print_confusion_matrix
    print("-\t-\t-\t-\t-\n")
    for t_i, t in enumerate(model.trees):
        # print("---tree[%d]---\n"%(t_i,))
        # print(t)
        truth = [e.label for e in examples]
        predictions = [ t.predict(e) for e in examples]
        legend, mat = confusion_matrix(truth, predictions)
        # legend, mat = training_confusion_matrix(t)
        correct, all = sum(mat[i][i] for i in range(len(legend))), sum(mat[i][j] for j in range(len(legend)) for i in range(len(legend)))
        # print_confusion_matrix(legend, mat)
        print("Training acc of tree[%d]: %d/%d = %f"%(t_i,correct, all, correct/all))
    print("-\t-\t-\t-\t-\n")

    predictions = [ model.predict(e) for e in examples]
    n_correct = sum(1 if predictions[i] == examples[i].label else 0 for i in range(len(examples)) )
    print("RandomForest training acc=%d/%d=%f" % (n_correct, len(examples), n_correct/len(examples)) )
        


def _print_decision_tree_summary(model: 'DecisionTree', examples:'List[Example]'):
    if model.tree_builder.leaf_builder.is_classification():
        print(model)
        truth = [e.label for e in examples]
        predictions = [ model.predict(e) for e in examples]
        legend, mat = confusion_matrix(truth, predictions)
        correct, all = sum(mat[i][i] for i in range(len(legend))), sum(mat[i][j] for j in range(len(legend)) for i in range(len(legend)))
        print_confusion_matrix(legend, mat)
        print("Accuracy: %d/%d = %f"%(correct, all, correct/all))
