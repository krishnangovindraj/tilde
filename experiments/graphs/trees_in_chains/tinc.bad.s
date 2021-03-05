tilde_mode(isolation_forest(30, 9, 5)).
typed_language(yes).

predict(graph(+key, -dummyclass)).

%max_lookahead(3).

type(edge(key, node, node)).
rmode(5: edge(+K, +-A, +-B)).
% lookahead(edge(K, A1, A2), edge(K, A1, A3)).
% lookahead(edge(K, A1, A2), edge(K, A3, A1)).
% lookahead(edge(K, A1, A2), edge(K, A2, A3)).
% lookahead(edge(K, A1, A2), edge(K, A3, A2)).


type(reachable(key, node, node)).
rmode(5: reachable(+K, +-A , +-B )).
% lookahead(reachable(K, A1, A2), reachable(K, A1, A3)).
% lookahead(reachable(K, A1, A2), reachable(K, A3, A1)).
% lookahead(reachable(K, A1, A2), reachable(K, A2, A3)).
% lookahead(reachable(K, A1, A2), reachable(K, A3, A2)).

special_test(unify_vars(node)).
special_test(diff_vars(node)).

