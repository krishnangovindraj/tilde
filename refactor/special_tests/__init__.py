from .real_number_leq_test import RealNumberLEQTest


# For the settings parser to create the right type of test
def create_from_settings_term(settings_term : 'problog.logic.Term'):
    if settings_term.functor == 'realtype_leq_test':
        assert(settings_term.arity == 1)
        real_typename = str(settings_term.args[0])
        return RealNumberLEQTest(RealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename, real_typename)
    else:
        raise ValueError("Unknown special_test" + settings_term.functor)
