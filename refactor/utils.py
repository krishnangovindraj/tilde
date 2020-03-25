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


from typing import Dict, List
from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_node import TreeNode
def training_accuracy(tree: DecisionTree):
    cm = training_confusion_matrix(tree)
    return (cm[0][0] + cm[1][1]) / (cm[0][0] + cm[1][1] + cm[0][1] + cm[1][0])

def training_confusion_matrix(tree: TreeNode):
    ccm = _training_confusion_matrix_recursive(tree)
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
