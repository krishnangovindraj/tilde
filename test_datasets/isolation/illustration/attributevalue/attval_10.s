tilde_mode(isolation_forest(80, 15, 40)).
typed_language(yes).

predict(example(+key, -dummyclass)).

type(instance(key, bool, bool, bool, bool, bool, bool, bool, bool, bool, bool)).
type(eq(bool,boolconst)).

rmode(10: instance(+K, -A1, -A2, -A3, -A4, -A5, -A6, -A7, -A8, -A9, -A10)).
rmode(10: eq(+B, #[1])).

max_lookahead(1).
lookahead(instance(K, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10), eq(A, C)).

%% special_test(unify_to_value(bool), eq).