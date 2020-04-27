tilde_mode(isolation_forest(25, 8, 5)).
predict(gaussian(+realnum_x, +realnum_y, -class), classification).

talking(3).
use_packs(0).
resume(off).
sampling_strategy(none).
heuristic(gain).

use_packs(0).
minfreq(0.2).

typed_language(yes).

special_test(rangerandom_realtype_leq_test(realnum_x, -50.0, +50.0)).
special_test(rangerandom_realtype_leq_test(realnum_y, -25.0, +25.0)).