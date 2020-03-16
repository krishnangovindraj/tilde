from .pythonstore_externalsubsumption_kb import PythonStoreForSubsumptionBasedGroundedKB



class SubtleGroundedKB(PythonStoreForSubsumptionBasedGroundedKB):

    SUBTLE_WRAPPER_PATH = 'test_datasets/theta-subsumption-engines/subtle/subtle-wrapper.pl'
    SUBTLE_QUERY_TEMPLATE = "subsumes_pyswip(%s, %s)"

    def __init__(self, bg_program_sp):
        super().__init__(bg_program_sp)
        self.encoded_bg = "false"    # str: "fact1,fact2,...,factn," # Yes, a trailing ,
        self._subtle = None

    def setup(self):
        from pyswip import Prolog
        self._subtle = Prolog()
        self._subtle.consult(self.SUBTLE_WRAPPER_PATH)
        super().setup()
        
    def _update_encoded_bg(self, facts):
        self.encoded_bg = ((", ".join(map( str, facts)) + "," + self.encoded_bg)).strip(",")
        
    """ Must return a dictionary of substitutions which can be used by problog.logic.Term.apply """
    def thetasubsumption(self, rule_body, db_extension=None):
        if db_extension is not None:
            db_string = "[%s]"%( (self.encoded_bg + "," + (", ".join(map( str, db_extension))) ))
        else:
            db_string =  "[%s]"%(self.encoded_bg)

        query_string = str(rule_body)
        
        subtle_query = self.SUBTLE_QUERY_TEMPLATE%(query_string, db_string) 
        return self._subtle.query(subtle_query)
