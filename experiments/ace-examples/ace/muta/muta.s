% tilde_mode(random_forest_classification(20, 0, 30)).
% tilde_mode(random_forest_classification(20, 0, 40)). % Decent ~80
% tilde_mode(random_forest_classification(20, 0, 30)). % DEcent only, ~77
% tilde_mode(random_forest_classification(20, 0, 0.6)). % Decent ~80 
% tilde_mode(random_forest_classification(20, 0, 0.4)).%  Also good  ~ 80
tilde_mode(random_forest_classification(5, 0, 30)).

use_packs(0).
resume(off).
sampling_strategy(none).
minimal_cases(4).
heuristic(gain).

% predict(dmuta(+mol,-class)).
predict(class(+mol,-class)).

typed_language(yes).
type(equals(X,Y)).
type(atom(mol, id, element, type, charge)).
type(sbond(mol, id, id, bondtype)).
type(molecule(mol)).
type(mymember(_,_)).


rmode(atom(+M, -A, -E, #[1,3,8,10,14,16,19,21,22,25,26,27,28,29,31,32,34,35,36,38,40,41,42,45,49,50,51,52,72,92,93,94,95,194,195,230,232], -Ch)).
rmode(atom(+M, -A, #[br,c,cl,f,h,i,n,o,s], -T, -Ch)).
rmode(atom(+M, -A, +-E, -T, -Ch)).
rmode(sbond(+M, +A1, +-A2, -BT)).

max_lookahead(1). 
lookahead(sbond(M,A1, A2, BT), ground_bondtype(BT, ACONST)).
lookahead(sbond(M,A1, A2, BT), atom(M, A2, ACONST, AVAR, BVAR)).
lookahead(sbond(M,A1, A2, BT), atom(M, A2, _, ACONST, _)).
lookahead(sbond(M,A1,A2,BT), sbond(M, A2, A3, _)).

special_test(unify_to_value(bondtype), ground_bondtype).
