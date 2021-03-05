tilde_mode(isolation_forest(40, 10, 15)).
predict(person(+pname, -dummyclass)).

talking(3).
use_packs(0).
resume(off).
sampling_strategy(none).
heuristic(gain).

use_packs(0).
minfreq(0.2).

typed_language(yes).

type(wealth(pname, wealthnum)).
type(friends(pname,pname)).

rmode(3: friends(+P, -Q)).
rmode(3: wealth(+P, -W)).

max_lookahead(3).
lookahead(friends(A,B), wealth(B,W)).
lookahead(wealth(P,W), wealth_leq(W,C) ).

% The jit version is incredibly slow here.
% special_test(jit_randomchoice_realtype_leq_test(wealthnum), wealth_leq).
special_test(randomchoice_realtype_leq_test(wealthnum), wealth_leq).
