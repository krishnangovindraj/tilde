tilde_mode(isolation_forest(30, 9, 5)).
typed_language(yes).

predict(example(+key, -dummyclass)).

type(instance(key, att1, att2, att3, att4, att5, att6)).
% In the simple Multi-instance setting (one key, many rows) we just need 1
rmode(1: instance(+K, -A1, -A2, -A3, -A4, -A5, -A6)).
% rmode(5: instance(+K, -A1, -A2, -A3, -A4, -A5, -A6)).

max_lookahead(1).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att1(A1, C)).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att2(A2, C)).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att3(A3, C)).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att4(A4, C)).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att5(A5, C)).
lookahead(instance(K, A1, A2, A3, A4, A5, A6), ground_att6(A6, C)).

special_test(unify_to_value(att1), ground_att1).
special_test(unify_to_value(att2), ground_att2).
special_test(unify_to_value(att3), ground_att3).
special_test(unify_to_value(att4), ground_att4).
special_test(unify_to_value(att5), ground_att5).
special_test(unify_to_value(att6), ground_att6).
