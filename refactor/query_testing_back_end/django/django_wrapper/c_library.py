import ctypes

try:
    lib_django = ctypes.CDLL('test_datasets/theta-subsumption-engines/django/libdjango.so')
except Exception as err:
    lib_django = None