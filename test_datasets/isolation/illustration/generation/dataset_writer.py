from typing import Dict, List, Tuple
from itertools import chain
class DatasetWriter:

    def __init__(self, example_pred_name='example', instance_pred_name='instance', dummyclass_name='dummyclass'):
        self.example_pred_name = example_pred_name
        self.instance_pred_name = instance_pred_name
        self.dummyclass_name = dummyclass_name

    def write_kb(self, examples: Dict[str, List[Tuple[str]]], file):
        sorted_keys = sorted(examples.keys())
        for k in sorted_keys: # chain(good_examples.keys(), bad_examples.keys()):
            print("%s(%s, %s)."%(self.example_pred_name, k, self.dummyclass_name) , file=file)
        print("", file=file)
        
        for k in sorted_keys:
            for instance in examples[k]:
                print("%s(%s, %s)."%(self.instance_pred_name, k, ', '.join(map(str,instance))), file=file)
            print(file=file)