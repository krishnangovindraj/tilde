from .real_number_leq_test import RealNumberLEQTest
from .randomchoice_real_leq import RandomChoiceRealNumberLEQTest
from .rangerandom_real_leq import RangeRandomRealNumberLEQTest

# For the settings parser to create the right type of test
def create_from_settings_term(special_test_term: 'Tuple[problog.logic.Term]', functor_name: str = None):
    if special_test_term.functor == 'realtype_leq_test':
        assert(special_test_term.arity == 1)
        real_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = RealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        
        return RealNumberLEQTest(functor_name, real_typename)

    elif special_test_term.functor == 'randomchoice_realtype_leq_test':
        assert(special_test_term.arity >= 1)
        real_typename = str(special_test_term.args[0])
        max_retries = int(special_test_term.args[1]) if special_test_term.arity >= 2 else RandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES
        if functor_name is None:
            functor_name = RandomChoiceRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        return RandomChoiceRealNumberLEQTest(functor_name, real_typename, max_retries)

    elif special_test_term.functor =='rangerandom_realtype_leq_test':
        assert(special_test_term.arity >= 3)
        real_typename = str(special_test_term.args[0])
        range_min, range_max = (float(special_test_term.args[1]), float(special_test_term.args[2]))
        max_retries = int(special_test_term.args[3]) if special_test_term.arity >= 4 else RandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES
        if functor_name is None:
            functor_name = RangeRandomRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        return RangeRandomRealNumberLEQTest(functor_name, real_typename, (range_min, range_max), max_retries)

    else:
        raise ValueError("Unknown special_test" + special_test_term.functor)
