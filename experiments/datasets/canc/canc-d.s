% Start Tilde with the command 'loofl(tilde,[1])'
% tilde_mode(random_forest_classification(20, 0, 0.6)).
tilde_mode(classify).

predict(canc_d(+drug,-class)).

classes([pos,neg]).
% max_lookahead(0).
discretize(equal_freq).
report_timings(on).
use_packs(cf_ilp).
sampling_strategy(none).
minimal_cases(2).
write_predictions([testing,distribution]).
m_estimate(m(2)).
tilde_rst_optimization(no).
exhaustive_lookahead(0).
query_batch_size(50000).

typed_language(yes).
type(atm_as(drug,atomid,atomtype,charge)).
type(atm_ba(drug,atomid,atomtype,charge)).
type(atm_br(drug,atomid,atomtype,charge)).
type(atm_c(drug,atomid,atomtype,charge)).
type(atm_ca(drug,atomid,atomtype,charge)).
type(atm_cl(drug,atomid,atomtype,charge)).
type(atm_cu(drug,atomid,atomtype,charge)).
type(atm_f(drug,atomid,atomtype,charge)).
type(atm_h(drug,atomid,atomtype,charge)).
type(atm_hg(drug,atomid,atomtype,charge)).
type(atm_i(drug,atomid,atomtype,charge)).
type(atm_k(drug,atomid,atomtype,charge)).
type(atm_mn(drug,atomid,atomtype,charge)).
type(atm_n(drug,atomid,atomtype,charge)).
type(atm_na(drug,atomid,atomtype,charge)).
type(atm_o(drug,atomid,atomtype,charge)).
type(atm_p(drug,atomid,atomtype,charge)).
type(atm_pb(drug,atomid,atomtype,charge)).
type(atm_s(drug,atomid,atomtype,charge)).
type(atm_se(drug,atomid,atomtype,charge)).
type(atm_sn(drug,atomid,atomtype,charge)).
type(atm_te(drug,atomid,atomtype,charge)).
type(atm_ti(drug,atomid,atomtype,charge)).
type(atm_zn(drug,atomid,atomtype,charge)).
type(sbond_1(drug,atomid,atomid)).
type(sbond_2(drug,atomid,atomid)).
type(sbond_3(drug,atomid,atomid)).
type(sbond_7(drug,atomid,atomid)).
% type(eq_atomtype(atomtype,atomtype)).
% type(eq_charge(charge,charge)).

rmode(atm_as(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_ba(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_br(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_c(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_ca(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_cl(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_cu(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_f(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_h(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_hg(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_i(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_k(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_mn(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_n(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_na(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_o(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_p(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_pb(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_s(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_se(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_sn(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_te(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_ti(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(atm_zn(+Drug0,+-Atomid1,-Atomtype2,-Charge3)).
rmode(sbond_1(+Drug0,+Atomid1,+-Atomid2)).
rmode(sbond_2(+Drug0,+Atomid1,+-Atomid2)).
rmode(sbond_3(+Drug0,+Atomid1,+-Atomid2)).
rmode(sbond_7(+Drug0,+Atomid1,+-Atomid2)).

% rmode(eq_atomtype(+X, #[1,10,101,102,113,115,120,121,129,134,14,15,16,17,19,191,192,193,2,21,22,232,26,27,29,3,31,32,33,34,35,36,37,38,40,41,42,45,49,499,50,51,52,53,60,61,62,70,72,74,75,76,77,78,79,8,81,83,84,85,87,92,93,94,95,96])).
% rmode(eq_charge(+X, #[charge_in_0175_0615,charge_in_1355_0175,charge_in_inf_1355,charge_in_0615_1375,charge_in_1375_inf])).
special_test(unify_to_value(charge), eq_charge).
special_test(unify_to_value(atomtype), eq_atomtype).



max_lookahead(0).
lookahead(sbond_1(M,A1,A2), atm_as(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_ba(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_br(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_c(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_ca(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_cl(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_cu(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_f(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_h(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_hg(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_i(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_k(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_mn(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_n(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_na(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_o(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_p(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_pb(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_s(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_se(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_sn(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_te(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_ti(M,A2, X, Y)).
lookahead(sbond_1(M,A1,A2), atm_zn(M,A2, X, Y)).

lookahead(sbond_3(M,A1,A2), atm_as(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_ba(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_br(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_c(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_ca(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_cl(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_cu(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_f(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_h(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_hg(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_i(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_k(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_mn(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_n(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_na(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_o(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_p(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_pb(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_s(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_se(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_sn(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_te(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_ti(M,A2, X, Y)).
lookahead(sbond_3(M,A1,A2), atm_zn(M,A2, X, Y)).

lookahead(sbond_2(M,A1,A2), atm_as(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_ba(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_br(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_c(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_ca(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_cl(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_cu(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_f(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_h(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_hg(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_i(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_k(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_mn(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_n(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_na(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_o(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_p(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_pb(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_s(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_se(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_sn(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_te(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_ti(M,A2, X, Y)).
lookahead(sbond_2(M,A1,A2), atm_zn(M,A2, X, Y)).

lookahead(sbond_7(M,A1,A2), atm_as(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_ba(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_br(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_c(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_ca(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_cl(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_cu(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_f(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_h(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_hg(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_i(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_k(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_mn(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_n(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_na(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_o(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_p(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_pb(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_s(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_se(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_sn(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_te(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_ti(M,A2, X, Y)).
lookahead(sbond_7(M,A1,A2), atm_zn(M,A2, X, Y)).

lookahead( atm_as(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_ba(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_br(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_c(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_ca(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_cl(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_cu(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_f(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_h(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_hg(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_i(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_k(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_mn(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_n(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_na(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_o(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_p(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_pb(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_s(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_se(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_sn(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_te(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_ti(M,A1, X, Y), sbond_1(M,A1,A2)).
lookahead( atm_zn(M,A1, X, Y), sbond_1(M,A1,A2)).

lookahead( atm_as(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_ba(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_br(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_c(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_ca(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_cl(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_cu(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_f(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_h(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_hg(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_i(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_k(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_mn(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_n(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_na(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_o(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_p(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_pb(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_s(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_se(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_sn(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_te(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_ti(M,A1, X, Y), sbond_3(M,A1,A2)).
lookahead( atm_zn(M,A1, X, Y), sbond_3(M,A1,A2)).

lookahead( atm_as(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_ba(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_br(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_c(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_ca(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_cl(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_cu(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_f(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_h(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_hg(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_i(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_k(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_mn(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_n(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_na(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_o(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_p(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_pb(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_s(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_se(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_sn(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_te(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_ti(M,A1, X, Y), sbond_2(M,A1,A2)).
lookahead( atm_zn(M,A1, X, Y), sbond_2(M,A1,A2)).

lookahead( atm_as(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_ba(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_br(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_c(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_ca(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_cl(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_cu(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_f(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_h(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_hg(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_i(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_k(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_mn(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_n(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_na(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_o(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_p(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_pb(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_s(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_se(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_sn(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_te(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_ti(M,A1, X, Y), sbond_7(M,A1,A2)).
lookahead( atm_zn(M,A1, X, Y), sbond_7(M,A1,A2)).


execute(loofl(tilde,[1])).
execute(quit).
