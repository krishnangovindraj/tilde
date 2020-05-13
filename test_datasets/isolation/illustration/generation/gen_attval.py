N_REGULAR = 84 # 44 if inverted 
N_OUTLIER = 2
N_VARIABLES = 7
FORMULA = [ [2,4,-6], [3, -5] ]
INVERT = False


from gen_dnf import DNFGenerator
from dataset_writer import DatasetWriter
from random import sample, shuffle


dgen = DNFGenerator(N_VARIABLES, FORMULA)

goodconj, badconj = dgen.generate_all()

# print(len(goodconj),len(badconj)); quit();

if INVERT:
    regulars = [ [x] for x in sample(goodconj, N_REGULAR) ]
    outliers = [ [x] for x in sample(badconj,  N_OUTLIER) ]
else:
    regulars = [ [x] for x in sample(badconj, N_REGULAR) ]
    outliers = [ [x] for x in sample(goodconj,  N_OUTLIER) ]

from math import ceil, log10
padding = ceil(log10(2**N_VARIABLES))
key_str = lambda x: dgen.binary2intstr(x, padding=padding) 


ds_dict = { 'e%s'%(key_str(val_list[0])) : val_list for i,val_list in enumerate(regulars) }
ds_dict.update({'o%s'%(key_str(val_list[0])) : val_list for i,val_list in enumerate(outliers) })

ds_writer = DatasetWriter()

print("%% %d regular and %d outliers ; total = %d"%(len(regulars), len(outliers), len(ds_dict)))
from sys import stdout
ds_writer.write_kb(ds_dict, file=stdout)