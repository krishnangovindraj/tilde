import ctypes

try:
    lib_django = ctypes.CDLL('/mnt/d/workcode/Django/libdjango.so')
except Exception as err:
    lib_django = None