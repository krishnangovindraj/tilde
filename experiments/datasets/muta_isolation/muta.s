tilde_mode(isolation_forest(40,10,10)).
use_packs(0).
resume(off).
sampling_strategy(none).
minimal_cases(4).
heuristic(gain).

predict(class(+mol,-class)).

typed_language(yes).
type(equals(bondtype,bondtype)).
type(atom(mol, id, element, type, charge)).
type(sbond(mol, id, id, bondtype)).
type(molecule(mol)).

max_lookahead(1). 
lookahead(sbond(M,A1, A2, BT), equals(BT,CT)).
lookahead(sbond(M,A1, A2, BT), atom(M, A2, C3, D4, E5)).
lookahead(sbond(M,A1, A2, BT), atom(M, A2, C3, D4, E5)).
lookahead(sbond(M,A1,A2,BT), sbond(M, A2, A3, B2)).

rmode(atom(+M, -A, -E, #[1,3,8,10,14,16,19,21,22,25,26,27,28,29,31,32,34,35,36,38,40,41,42,45,49,50,51,52,72,92,93,94,95,194,195,230,232], -Ch)).
rmode(atom(+M, -A, #[br,c,cl,f,h,i,n,o,s], -T, -Ch)).
rmode(atom(+M, -A, +-E, -T, -Ch)).
rmode(sbond(+M, +A1, +-A2, -BT)).
rmode(equals(+BT,#[1,2,3,4,5,7])).

