predict(realtest(+realnum_x, -class), classification).

talking(3).
use_packs(0).
resume(off).
sampling_strategy(none).
heuristic(gain).

use_packs(0).
minfreq(0.2).

typed_language(yes).

special_test(jit_realtype_leq_test(realnum_x), realnum_x_leq).
