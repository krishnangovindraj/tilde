% retry-hax is the original subtle code with the cut in processCC/2 commented out.
% The original subtle code can be obtained from: https://dtai.cs.kuleuven.be/software/subtle/
:- use_module('subtle-2.2.pl').

% pyswip hax: Apply the substitution.
substitution_apply_for_pyswip([]).
substitution_apply_for_pyswip([SubHead|SubTail]):-
	SubHead = X/X,
	substitution_apply_for_pyswip(SubTail).

subsumes_pyswip(C1, C2):-
	subsumes_for_pyswip(C1, C2, Sub),
	substitution_apply_for_pyswip(Sub).
