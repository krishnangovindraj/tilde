predict(specialnum(+num, -class)).

typed_language(yes).
type(divides(num, num, num)).

special_test(unify_to_value(num), unify_num).

rmode(3: divides(+N, -P, -M)).
lookahead(divides(A,B,C), unify_num(B, D)).