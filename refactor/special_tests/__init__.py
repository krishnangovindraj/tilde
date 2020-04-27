from .real_number_leq_test import RealNumberLEQTest
from .randomchoice_real_leq import RandomChoiceRealNumberLEQTest
from .rangerandom_real_leq import RangeRandomRealNumberLEQTest

# For the settings parser to create the right type of test
def create_from_settings_term(settings_term : 'problog.logic.Term'):
    if settings_term.functor == 'realtype_leq_test':
        assert(settings_term.arity == 1)
        real_typename = str(settings_term.args[0])
        return RealNumberLEQTest(RealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename, real_typename)

    elif settings_term.functor == 'randomchoice_realtype_leq_test':
        assert(settings_term.arity >= 1)
        real_typename = str(settings_term.args[0])
        max_retries = int(settings_term.args[1]) if settings_term.arity >= 2 else RandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES  
        return RandomChoiceRealNumberLEQTest(RandomChoiceRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename, real_typename, max_retries)

    elif settings_term.functor =='rangerandom_realtype_leq_test':
        assert(settings_term.arity >= 3)
        real_typename = str(settings_term.args[0])
        range_min, range_max = (float(settings_term.args[1]), float(settings_term.args[2]))
        max_retries = int(settings_term.args[3]) if settings_term.arity >= 4 else RandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES  
        return RangeRandomRealNumberLEQTest(RangeRandomRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename, real_typename, (range_min, range_max), max_retries)

    else:
        raise ValueError("Unknown special_test" + settings_term.functor)
