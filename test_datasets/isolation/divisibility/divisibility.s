tilde_mode(isolation_forest(50, 15, 15)).
predict(specialnum(+num, -class)).

typed_language(yes).
type(divides(num, num, num)).
type(unify(num, num)).

rmode(3: divides(+N, -+P, -M)).
% rmode(3: unify(+X,#[2,3,5,7,11,13,17,19,23,29,31,37])).

% lookahead(divides(X,Y,Z), unify(Y,P)).

% This goes and does large numbers which kinda suck. But with the simple splitter, maybe.
rmode(3: unify(+X,+Y)).
special_test(unify_to_value(num)).
