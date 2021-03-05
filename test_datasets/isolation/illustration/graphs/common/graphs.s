tilde_mode(isolation_forest(20, 40, 100)).
typed_language(yes).

predict(graph(+key, -dummyclass)).


type(edge(key, node, node)).
% rmode(5: edge(+K, +-A, +-B)).
rmode(5: edge(+K, +-A, +-B)). % This is simpler. Let unify handle the unification

type(reachable(key, node, node)).
% rmode(5: reachable(+K, +-A , +-B )).
rmode(5: reachable(+K, +-A , -B )). % This is simpler. Let unify handle the unification

%special_test(unify_vars(node), unify_nodes).
special_test(diff_vars(node), diff_nodes).


max_lookahead(0).
% % Lots of lookahead needed
lookahead(edge(K, A1, A2), edge(K, A3, A4)).
%lookahead(edge(K, A1, A2), reachable(K, A3, A4)).
%lookahead(reachable(K, A1, A2), edge(K, A3, A4)).
%lookahead(reachable(K, A1, A2), reachable(K, A3, A4)).

%lookahead(edge(K, A1, A2), unify_nodes(X, Y)).
lookahead(edge(K, A1, A2), diff_nodes(X, Y)).
%lookahead(reachable(K, A1, A2), unify_nodes(X, Y)).
%lookahead(reachable(K, A1, A2), diff_nodes(X, Y)).

%lookahead(unify_nodes(X,Y), diff_nodes(A,B)).
