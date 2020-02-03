## This is mainly so I don't forget what I was planning.

We want to get all groundings of a single rule which can pop-up during the course of tree construction.
Since every grounding must (practically, not theoretically) be reachable through a chain of variables starting from an example, 
we will use the examples to bound our search. We also exploit the typed language.


IGNORE 
        ( For now, I assume no A-B recursion )
        Define the type-dependency DAG as follows
        * Nodes are mode declarations.
        * There is an edge from A to B if a variable of type T which is introduced by A is used in B
            - Typically, -T is an arg of A  and +T is an arg of B ) 
/IGNORE


Whenever a new variable X of type T is introduced, Every mode which has a +T arg must be evaluated with X as argument.   


Algo:

foreach example E:
    seen_vars = {}
    new_vars = { (T,X)  | T is the type of an argument with value X in E }

    while !new_vars.empty():
        (T,X) = new_vars.pop()
        foreach mode which has an arg of form +T:
            evaluate every combination of arguments in seen_vars + (T,X) where atleast one argument is (T,X)
            for every (T',X') (not in seen_vars) introduced in the evaluation, add (T',X') to new_vars
            add (T,X) to seen_vars
    

To produce all groundings for a certain rule:
1. Use all mode declarations for which groundings are available (facts and processed rules) - 

2.  ForEach example:
