tilde_mode(isolation_forest(40, 8, 30)).
predict(person(+pname, -dummyclass)).

typed_language(yes).

type(nationality(pname,country)).
type(friends(pname,pname)).
type(continent(country,continentname)).

rmode(3: friends(+P, -Q)).
rmode(3: nationality(+P, -N)).
rmode(3: continent(+N, #[asia,europe])).

max_lookahead(4).
lookahead(friends(A,B), nationality(B,N)).
lookahead(nationality(P,N), continent(N,C)).

special_test(unify_to_value(country), unify_country).