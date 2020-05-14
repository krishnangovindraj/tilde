
# For the settings parser to create the right type of test
def create_from_settings_term(special_test_term: 'Tuple[problog.logic.Term]', functor_name: str = None):


    # JIT tests are a decent idea if you have a huge number of small examples.
    # If you have a small number of huge examples, pro-active is better

    if special_test_term.functor == 'realtype_leq_test':
        from .real_number_leq_test import RealNumberLEQTest
        assert(special_test_term.arity == 1)
        real_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = RealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename

        return RealNumberLEQTest(functor_name, real_typename)

    elif special_test_term.functor == 'randomchoice_realtype_leq_test':
        from .randomchoice_real_leq import RandomChoiceRealNumberLEQTest

        assert(special_test_term.arity >= 1)
        real_typename = str(special_test_term.args[0])
        max_retries = int(special_test_term.args[1]) if special_test_term.arity >= 2 else RandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES
        if functor_name is None:
            functor_name = RandomChoiceRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        return RandomChoiceRealNumberLEQTest(functor_name, real_typename, max_retries)

    elif special_test_term.functor =='rangerandom_realtype_leq_test':
        from .jit.jit_rangerandom_real_leq import JitRangeRandomRealNumberLEQTest

        assert(special_test_term.arity >= 3)
        real_typename = str(special_test_term.args[0])
        range_min, range_max = (float(special_test_term.args[1]), float(special_test_term.args[2]))
        max_retries = int(special_test_term.args[3]) if special_test_term.arity >= 4 else JitRangeRandomRealNumberLEQTest.DEFAULT_MAX_RETRIES
        if functor_name is None:
            functor_name = JitRangeRandomRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        return JitRangeRandomRealNumberLEQTest(functor_name, real_typename, (range_min, range_max), max_retries)

    elif special_test_term.functor == 'unify_to_value':
        from .unify_to_value import UnifyToValueTest
        assert(special_test_term.arity >= 1)
        target_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = UnifyToValueTest.TEST_FUNCTOR_PREFIX + target_typename

        return UnifyToValueTest(functor_name, target_typename)

    elif special_test_term.functor == 'unify_vars':
        from .unify_variables import UnifyVariablesTest
        assert(special_test_term.arity >= 1)
        target_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = UnifyVariablesTest.TEST_FUNCTOR_PREFIX + target_typename

        return UnifyVariablesTest(functor_name, target_typename)

    elif special_test_term.functor == 'diff_vars':
        from .differentiate_variables import DifferentiateVariablesTest
        assert(special_test_term.arity >= 1)
        target_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = DifferentiateVariablesTest.TEST_FUNCTOR_PREFIX + target_typename

        return DifferentiateVariablesTest(functor_name, target_typename)


    elif special_test_term.functor == 'jit_realtype_leq_test':
        from .jit.jit_real_leq_test import JitRealNumberLEQTest
        assert(special_test_term.arity == 1)
        real_typename = str(special_test_term.args[0])
        if functor_name is None:
            functor_name = JitRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename

        return JitRealNumberLEQTest(functor_name, real_typename)

    elif special_test_term.functor == 'jit_randomchoice_realtype_leq_test':
        from .jit.jit_randomchoice_real_leq import JitRandomChoiceRealNumberLEQTest

        assert(special_test_term.arity >= 1)
        real_typename = str(special_test_term.args[0])
        max_retries = int(special_test_term.args[1]) if special_test_term.arity >= 2 else JitRandomChoiceRealNumberLEQTest.DEFAULT_MAX_RETRIES
        if functor_name is None:
            functor_name = JitRandomChoiceRealNumberLEQTest.TEST_FUNCTOR_PREFIX + real_typename
        return JitRandomChoiceRealNumberLEQTest(functor_name, real_typename, max_retries)

    else:
        raise ValueError("Unknown special_test " + special_test_term.functor)
