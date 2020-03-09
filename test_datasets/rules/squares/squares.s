predict(specialnum(+num, -class), classification).

typed_language(yes).
type(divides(num, num, num)).
type(unify(num, num)).
lookahead(divides(X,Y,Z), unify(Y,Z)).

rmode(3: divides(+N, -+P, -M)).
rmode(3: unify(+X,+Y)).