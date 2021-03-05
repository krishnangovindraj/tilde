tilde_mode(isolation_forest(40, 15, 40)).
typed_language(yes).

predict(example(+key, -dummyclass)).

type(instance(key, bool, bool, bool, bool, bool, bool, bool, bool)).
type(eq(bool,boolconst)).

rmode(8: instance(+K, -A1, -A2, -A3, -A4, -A5, -A6, -A7, -A8)).
rmode(8: eq(+B, #[1])).

max_lookahead(1).
lookahead(instance(K, A1, A2, A3, A4, A5, A6, A7, A8), eq(A, C)).

%% special_test(unify_to_value(bool), eq).