
from enum import Enum as _Enum
class BackendChoice(_Enum):
    PROBLOG = 'problog-simple'
    SUBTLE = 'subtle'
    DJANGO = 'django'

    @staticmethod
    def from_value(value_str):
        vl = [m for m in BackendChoice.__members__  if BackendChoice.__members__[m].value==value_str]
        return BackendChoice.__members__[vl[0]] if len(vl) == 1 else None
